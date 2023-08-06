# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

class Categoriser(dict):

    def __init__(self,header,format,categorise,series=(),parallel=(),initial_categories=()):
        """categorises rows and then hands off to other processors.
        This can be used for things like splitting into categories or
        showing the most popular pages.
        
        header - the header printed at the top of the output generated
                 by formatted().
        format - the format string for displaying the category, names
                 available are:
                 category - the name of the category to be displayed
                 percentage - the percentage this category forms of
                              the overall number of rows this
                              categoriser has processed.
                 count - the number of rows in this category
                 total - the total number of rows processed by this
                         categoriser. 
                 formatted - the combined result of calling the formatted
                             method of any anything in series or
                             parallel. 
        categorise - a callable that takes a row as a paramter
                     and returns a string category name.
        parallel - a tuple of 'processor tuples'. The output of each processors
                   will be returned in formatted() side-by side.
        series - a tuple of 'processor tuples'. The output of each processor
                 will be displayed one after the other in formatted().
                 
        Each processor tuple contains something like:

        (class,class_args,formatted_kw,categories)

        class - a processor class

        class_args - the args used to instantiate the processor class

        formatted_kw - the keyword parameters passed to the
                       processor's formatted method when it's called.

        categories - a tuple of categories to which this processor
                     will be applied. If Empty, it will apply to all
                     categories.
                     
        One of each type of processor is created for each category.

        As an example of how the elements of a processor tuple
        interract:

        print class(*class_args).formatted(**formatted_kw)
        
        """
        self.header = header
        self.format = format
        self.categorise = categorise
        self.total = 0.0
        self.parallel = parallel
        self.series = series
        for category in initial_categories:
            self.createCategory(category)        

    def createCategory(self,category):
            self[category] = [0.0]
            processors = []
            try:
                for klass,klass_args,formatted_kw,categories in self.series:
                    if category in categories or not categories:
                        processors.append((klass(*klass_args),formatted_kw))
            except (ValueError,TypeError),e:
                raise RuntimeError('Incorrect series format: %s for %s' % (e,repr(self.series)))
            self[category].append(processors)
            processors = []
            try:
                for klass,klass_args,formatted_kw,categories in self.parallel:
                    if category in categories or not categories:
                        processors.append((klass(*klass_args),formatted_kw))
            except (ValueError,TypeError),e:
                raise RuntimeError('Incorrect parallel format: %s for %s' % (e,repr(self.parallel)))
            self[category].append(processors)
        
    def process(self,obj):
        category = self.categorise(obj)
        if not self.has_key(category):
            self.createCategory(category)
        self[category][0] += 1
        for processor,junk in (self[category][1]+self[category][2]):
            processor.process(obj)
        self.total += 1


    def formatted(self,keys=None,sort='key',reverse=True,cutoff=None):
        """
        keys - specifies whcih categories to display
        sort - what to sort on, can be one of:
            key - the name of the category
            percentage - the percentage this category forms of all
                     rows seen by this categoriser
            count - the count of rows in this category
        """
        p_keys = keys
        keys = p_keys or self.keys()
        result = []
        for key in keys:
            # skip keys that have nothing stored for them
            if not self.has_key(key):
                continue
            try:
                percentage = 100*self[key][0]/self.total
            except ZeroDivisionError:
                percentage = -1
            formatted = []
            columns = []
            max_lens = []
            column_rows = []
            row_count = 0
            # parallel
            
            for processor,kw in self[key][2]:
                columns.append(processor.formatted(**kw))
                
            for column in columns:
                max_lens.append(0)
                column_rows.append([])
                rows = column.split('\n')
                l = len(rows)
                if l>row_count:
                    row_count = l
                for row in rows:
                    l = len(row)
                    if l>max_lens[-1]:
                        max_lens[-1]=l
                    column_rows[-1].append(row)
                    
            for i in range(row_count):
                combined_row = ''
                for j in range(len(column_rows)):
                    column = column_rows[j]
                    column_width = max_lens[j]
                    blank_row = (column_width+1)*' '
                    row_format = '%-'+str(column_width)+'s '
                    try:
                        row = column[i]
                    except IndexError:
                        combined_row += blank_row
                        continue
                    combined_row += (row_format % row)
                formatted.append(combined_row)

            if formatted:
                formatted = [('\n'.join(formatted))]
                
            # series
            for processor,kw in self[key][1]:
                formatted.append(processor.formatted(**kw))

            # overall
            result.append({'key':key,
                           'percentage':percentage,
                           'count':self[key][0],                       
                           'value': self.format % {
                                       'category':key,
                                       'percentage':percentage,
                                       'count':self[key][0],
                                       'total':self.total,
                                       'formatted':'  '+('\n  '.join(('\n\n'.join(formatted)).split('\n'))),
                                       'raw':(' '.join(formatted)).strip(),
                                       }})
        if not p_keys:
            # only sort if no keys have been passed in, so we can give a non-standard sort
            result.sort(lambda x,y: cmp(x[sort],y[sort]))
        if reverse:
            result.reverse()
        l_result = len(result)
        if cutoff and l_result > cutoff:
            result = result[:cutoff]
            result.append({'value':'%i rows not shown' % (l_result-cutoff)})
        return (self.header and self.header+'\n' or '')+'\n'.join([r['value'] for r in result])
