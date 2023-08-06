import scipy, numpy, csv, itertools
from datetime import date
from pylab import linspace
import matplotlib.pyplot as mp
DEBUG = 0

## Exception Classes for Dataframe##
class DataframeException(Exception):
    """Base class exception for Dataframe"""
    def __init__(self,):
        print "some issue with data frame"

class RowHeaderException(DataframeException):
    def __init__(self):
        print "Some problem with Row Header"
class ColumnHeaderException(DataframeException):
    def __init__(self):
        print "Some problem with Column Header"

class DataException(DataframeException):
    def __init__(self, text = None):
        print "Some problem with Data"
        self.text = text
    def __str__(self):
        return repr(self.text)
    
class ToBeImplemented(DataframeException):
    def __init__(self):
        print "Not yet implmented"

## Class for dataframe ##
class Dataframe(object):
    """
    This is the base frame that holds flat 2 dimensional data
    """
    def __init__(self, data = None, columnList = None, rowList = None):
        """
        :para data: either list of list of float or scipy.matrix
        :para columnList: list<String> for the column header
        """
        self.data = scipy.matrix(data)
        if not rowList: self.rowHeader(rowList)
        if not columnList: self.columnHeader(columnList)
        pass
    def __str__(self):
        data = self.data.tolist()
#        print data
        def hellipsis(li):
            string = ""
            if len(li) > 6:
                for i in li[:3]:
                    string += (str(i)+"\t")
                string += "..."
                for i in li[-3:]:
                    string += ("\t"+str(i))
                return string
            else:
                for i in li:
                    string += (str(i)+"\t")
                return string
            
        string = ""
        for i in data:
            string+=(hellipsis(i)+"\n")
        return string

    def plot(self):
        """
        Plot the cumulated weight, it was quickly implemented to plot the result. It is unsafe.
        """
        c = self.data.T.copy()
        for index in xrange(len(c.T)):
            c[:, index] /= sum(c[:,index])
        c = numpy.add.accumulate(c, axis = 0).tolist()
        x = [(float(i)+0.5/(len(self.data)))/float(len(self.data)) for i in range(len(self.data))]
        fig = mp.figure(num = None, figsize = (12,9), facecolor='w')
        ax = fig.add_subplot(111)
        colors = ["#FF0000",
                  "#00FFFF",
                  "#0000FF",
                  "#0000A0",
                  "#FF0080",
                  "#800080",
                  "#FFFF00", 
                  "#00FF00", 
                  "#FF00FF", 
                  "#C0C0C0", 	
                  "#808080", 
                  "#FF8040", 
                  "#804000",
                  "#800000",
                  "#808000", 
                  "#408080"]
    
        ax.fill_between(x,c[0], facecolor = colors[0], label = self.cheader[0])
        xi = linspace(0,1,100)
        for i in xrange(1,len(c), 1):
            ax.fill_between(x, 
                            c[i], 
                            c[i-1],
                            facecolor = colors[i],
                            label = self.cheader[i])
        legendRec = []
        from matplotlib.patches import Rectangle
        r = Rectangle((0, 0), 1, 1) # creates rectangle patch for legend use.
        for i in xrange(len(c)):
            legendRec.append(Rectangle((0, 0), 1, 1, fc = colors[i])) # creates rectangle patch for legend use.
        ax.legend(legendRec, self.cheader[:len(c)], loc = (0.9,0.5), shadow=True, fancybox=True) # ;
        ax.axis([0.0, 1.1, 0, 1])
        ax.grid(True)
        mp.show()
    

    def size(self):
        """
        Return shape of the data.
        :return: the dimensions of the data.
        :rtype: tuple(int, int)
        """
        return scipy.shape(self.data)
            
    def rowHeader(self, headerList):
        """
        :param headerList: List of header for the rows
        :type headerList: list<String>
        """
        try:
            self.rheader = list(headerList)
        except:
            raise RowHeaderException

    def columnHeader(self, headerList):
        """
        :param headerList: List of header for the columns
        :type headerList: list<String>
        """
        if isinstance(headerList, str):
            self.cheader = [headerList]
        else:
            try:
                self.cheader = list(headerList)
            except:
                raise ColumnHeaderException

    def summary(self):
        """
        Return the summary of the underlying data. *Not yet implemented*
        """
        raise ToBeImplemented

    def toCSV(self, name = "default.csv"):
        """
        Export the data into comma seperated value (CSV) format
        :param name: The name of the file to be exported.
        :type name: String
        """
        import csv 
        csvReader = csv.writer(open(name, 'w'), dialect='excel')
        for i in self.data.tolist():
            csvReader.writerow(i)
        del csvReader

    def __len__(self):
        """
        Return number of time series it has
        """
        return len(self.rheader)


## Class for TimeSeriesFrame derived from Dataframe ##

class TimeSeriesFrame(Dataframe):
    i = 0                       # Counter for RowIterator
    ci = 0                      # Counter for ColumnIterator
    def __init__(self, data = None, rowList = None, columnList = None, rown = None, coln = None):
        """
        Constructor

        :param data: Matrix with time series in columns
        :type data: scipy.matrix
        :param rowList: list of row headers
        :type rowList: list<String>
        :param columnList: list of column headers
        :type columnList: list<String>
        """
        size = scipy.shape(data)
        if size[0] < 1 or size[1] < 1:
            raise DataException("Your data dimension sucks ass")
        try:
            self.data = scipy.matrix(data)
        except:
            raise DataException        
        if rowList != None: self.rowHeader(rowList)
        if columnList != None: self.columnHeader(columnList)
        if coln and columnList == None:
            self.columnHeader(map(str, range(len(self.data[0]))))
        
    def __getitem__(self, key):
        """
        Valid Syntax
        stock[:,1],
        stock[:, n:m:r],
        stock[date1:date2],
        stock[date1:date2,:],
        stock[date1:date2, n:m:r]
        stock[date]
        """
        def getIndex(l, key):
#            for i in l: print i
            if key == None:
                return None
            try:
                return l.index(key)
            except:
                if min(l) > key or max(l) < key:
                    raise IndexError
                else:
                    for i in xrange(len(l)):
                        if l[i] > key:
                            return i
        #implement single index
        if DEBUG: print "KEY: ",  key
        if isinstance(key, date): # check stock[date]
            if DEBUG: 
                print "if isinstance(key, date):"
            key = getIndex(self.rheader, key)
            return TimeSeriesFrame(self.data[key], self.rheader[key], self.cheader)
        if isinstance(key, slice): # check stock[date1:date2]
            if isinstance(key.start, date) or isinstance(key.stop, date):
                key = slice(getIndex(self.rheader,key.start), getIndex(self.rheader,key.stop))
            return TimeSeriesFrame(self.data[key], self.rheader[key], self.cheader)
        elif len(key) > 2:      # allow two dimensions
            raise DataframeException
        else:
            if isinstance(key[0].start, date) or isinstance(key[0].stop, date): #stock[date1:date2,:], stock[date1:date2, n:m:r]
                if DEBUG: print "in isinstance(key[0].start, date) or isinstance(key[0].stop, date): "
                key = list(key)
                key[0] = slice(getIndex(self.rheader,key[0].start), getIndex(self.rheader,key[0].stop))
                key = tuple(key)
            return TimeSeriesFrame(self.data[key], self.rheader[key[0]], self.cheader[key[1]])

      
    def __str__(self):
        """Need to be rewritten"""
        size = self.size()
        if DEBUG: print "size: ", size
        if size[0] >6 and size[1] > 6:
            if DEBUG: print " size[0] >6 and size[1] > 6:"
            cstring = "\t\t"
            for i in self.cheader[:3]: cstring +=(str(i)+", ")
            cstring +="..., "
            for i in self.cheader[-3:]: cstring +=(str(i)+", ")
            bodystring =cstring+"\n"
            for n,i in enumerate(self.data[:3,:]):
                tempstring = (str(self.rheader[n]) + "\t")
                for j in i[:,:3]:
                    tempstring += (str(j).strip('[').strip(']')+",")
                tempstring += "..., "
                for j in i[:,-3:]: 
                    tempstring += (str(j).strip('[').strip(']'))+","
                bodystring += (tempstring +"\n")
            bodystring += "..., \t \t ..., \n"
            for n,i in enumerate(self.data[-3:]):
                tempstring = (str(self.rheader[-(3-n)])+"\t")
                for j in i[:,:3]:
                    tempstring += (str(j).strip('[').strip(']'))+", "
                tempstring += "..., "
                for j in i[:,-3:]:
                    tempstring += (str(j).strip('[').strip(']'))+", "
                bodystring += (tempstring +"\n")
            return bodystring
        if size[0] <= 6 and size[1] <= 6:
            if DEBUG: print "if size[0] <= 6 and size[1] <= 6:"
            cstring = "\t\t" + ", ".join(self.cheader)
#            cstring +=(str(i) + " ")
            bodystring =cstring+"\n"
            for n, i in enumerate(self.data):
                tempstring = (str(self.rheader[n]) + "\t")
                tempstring += (str(i).strip('[').strip(']')+",")
            return bodystring+tempstring+"\n\n"
        if size[1]<=6:
            if DEBUG: print "In size[1]<=6"
            cstring = "\t\t" + ", ".join(self.cheader)
            bodystring =cstring+"\n"
            for n,i in enumerate(self.data[:3,:]):
                tempstring = (str(self.rheader[n]) + "\t")
                for j in i[:,:]:
                    tempstring += (str(j).strip('[').strip(']')+",")
                bodystring += (tempstring +"\n")
            if size[0] > 6:
                bodystring += "...\t\t...\t\t...\n"
            for n,i in enumerate(self.data[-3:]):
                tempstring = (str(self.rheader[-(3-n)])+"\t")
                for j in i[:,:]:
                    tempstring += (str(j).strip('[').strip(']'))+", "
                bodystring += (tempstring +"\n")
            return bodystring
        if size[0] <= 6 and size[1] > 6:
            if DEBUG: print " size[0] <= 6 and size[1] > 6:"
            cstring = "\t\t"
            for i in self.cheader[:3]: cstring +=(str(i)+", ")
            cstring +="..., "
            for i in self.cheader[-3:]: cstring +=(str(i)+", ")
            bodystring =cstring+"\n"
            for n,i in enumerate(self.data[:,:]):
                tempstring = (str(self.rheader[n]) + "\t")
                for j in i[:,:3]:
                    tempstring += (str(j).strip('[').strip(']')+",")
                tempstring += "..., "
                for j in i[:,-3:]: 
                    tempstring += (str(j).strip('[').strip(']'))+","
                bodystring += (tempstring +"\n")
            return bodystring

#        __str__ = __repr__
        
    def rowHeader(self, headerList):
        try:
            if isinstance(headerList, date):
                self.rheader = [headerList]
            elif all(map(lambda x:isinstance(x, date), headerList)):
                self.rheader = list(headerList)
        except:
            raise RowHeaderException

    def columnIterator(self):
        """ 
        This is a generator to iterate across different time series
        
        :rtype: TimeSeriesFrame
        """

        while self.ci<self.size()[1]:
            yield self[:,self.ci]
            self.ci += 1
        else:
            self.ci = 0
            raise StopIteration

    def rowIterator(self):
        """ 
        This is a generator to iterate all the time series by date

        :rtype: TimeSeriesFrame
        """        
        while self.i < len(self.rheader):
            yield TimeSeriesFrame(self.data[self.i], self.rheader[self.i], self.cheader)
            self.i+=1
        else:
            self.i = 0
            raise StopIteration

def StylusReader(writer):
    """
    A simple parse function that read the the output of the internal software that I work with.
    
    :param writer: csv.writer object
    :type writer: csv.writer
    :return: the data wrapped in timeSeriesFrame
    :rtype: TimeSeriesFrame
    """
    def toDate(element):
        try:
            element = map(int, element.split("/"))
        except:
            print "Element", element
#            element = map(int, element.split("/"))

        if element[2] <= 10:
            element[2] += 2000
        elif 10<=element[2]<=99:
            element[2] += 1900
        try:
            return date(element[2], element[0], element[1])
        except:
            print element

    writer = list(writer)
    c = writer.pop(0)[1:]
    writer = map(list, zip(*writer))
    r = map(toDate, writer.pop(0))
    for i in xrange(len(writer)):
        writer[i] = map(float, writer[i])
    data = scipy.transpose(scipy.matrix(writer))
    return TimeSeriesFrame(data, r,c)

# def windows(iterable, length=2, overlap = 0):
#     it = iter(iterable)
#     results = list(itertools.islice(it,length))
#     while len(results) == length:
#         yield scipy.matrix(results)
#         results = results[length - overlap:]
#         results.extend(itertools.islice(it, length-overlap))
#     if results:
#         yield scipy.matrix(results)
        
if __name__ =="__main__":
    stock_data = list(csv.reader(open("simulated_weight.csv", "rb")))
#    print stock_data
#    import code; code.interact(local=locals())

#    lipper_data = list(csv.reader(open("t_lipper_daily.csv", "rb")))    
    stock = StylusReader(stock_data)

#     #stock.StylusReader(stock_data)
#     try: print stock
#     except: print "stock"
#     try: print stock[:,1]
#     except: print "stock[:,1]"
#     try: print stock[:, 1:7]
#     except: print "stock[:, 1:7]"
#     try:
#         from datetime import date
#         print "stock[date(2001,1,1):date(2002,1,1)]"
#         print stock[date(2001,1,1):date(2002,1,1)]
#     except:
#         pass
#     print "stock[date(2001,1,1):date(2002,3,1),:]"
#     print stock[date(2001,1,1):date(2002,3,1),:]

#     try: print stock[date(2001,1,1):date(2002,1,1),1:6]
#     except: print "stock[date(2001,1,1):date(2002,1,1),1:6]"
#     try: print stock[date(2001,1,1)]
#     except: 
#         print "stock[date(2001,1,1)]"
#         print_exc_plus()
    
    stock.plot()
