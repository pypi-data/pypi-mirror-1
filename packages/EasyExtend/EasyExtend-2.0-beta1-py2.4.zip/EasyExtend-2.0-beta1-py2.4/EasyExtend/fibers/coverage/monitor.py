'''
The Monitor module implements objects used to perform code-coverage and visualisation.
'''
import sys

def measurement(nbr):
    '''
    Basic sensor function. A call of this function will be compiled into
    Python stmt blocks. Note that the vars attribute is not used yet.
    '''
    try:
        s = Monitor().sensors[nbr]
        s.done = True
        s.vars = sys._getframe(1).f_locals
    except IndexError:
        raise ValueError("no measurement data available for %d"%nbr)

class Monitor:
    single = None
    def __init__(self):
        if Monitor.single:
            self.__dict__ = Monitor.single.__dict__
        else:
            self.sensors   = []
            self.modules   = []
            Monitor.single = self

    def assign_sensors(self, module):
        if self.modules:
            last_mod = self.modules[-1]
            last_mod[1][1] = len(self.sensors)
            self.modules.append((module,[len(self.sensors),0]))
        else:
            self.modules.append((module,[0,0]))

    def check_on_covered(self, mod):
        f = file(mod[0])
        lines = f.readlines()
        begin, end = mod[1]
        to_check    = []
        uncovered   = []
        sensorlines = []
        for sensor in self.sensors[begin:end]:
            sensorlines.append(sensor.suite_begin)
            if not sensor.done:
                to_check.append(sensor)
            else:
                for s in to_check:
                    if sensor.suite_begin<s.suite_end:   # included -> suite entered
                        if sensor.suite_end<s.suite_end: # end-sensor did not respond
                            k = s.suite_end  # the suite-end may not be the accurate place
                                             # it can include comments and empty lines
                            while 1:
                                l = lines[k-1]
                                l = l.strip()
                                # print "DEBUG line: ", k,l
                                if len(l)==0 or l.startswith('#'):
                                    k-=1
                                else:
                                    break
                            sensorlines.append(k)
                            uncovered.append(k)
                            s.done = True
                        else:
                            s.done = True
                    else:
                        uncovered.append(s.suite_begin)
                        s.done = True
            to_check = [s for s in to_check if not s.done]
        for s in to_check:
            uncovered.append(s.suite_begin)
        return lines, sensorlines, uncovered


    def show_report(self, show_sensor=True, out=sys.stdout):

        def write_status():
            out.write("\n"+(13+len_f)*"-"+".\n")
            out.write(("Status:%%-%ds|\n"%(len_f+6))%" ")
            out.write(("%%-%ds|\n"%(len_f+13))%created)
            out.write(("%%-%ds|\n"%(len_f+13))%not_responded)
            out.write((13+len_f)*"-"+"'\n")

        def write_resume():
            out.write("\n========================================================================================\n")
            out.write("Summary:\n  %d sensors created\n  %d sensors did not respond\n\n"%(len(self.sensors),all_uncovered))
            out.write("========================================================================================\n")

        logo = []
        logo.append(r"     _____")
        logo.append(r"    /  __ \ ")
        logo.append(r"    | /  \/ _____   _____ _ __ __ _  __ _  ___")
        logo.append(r"    | |    / _ \ \ / / _ \ '__/ _` |/ _` |/ _ \ ")
        logo.append(r"    | \__/\ (_) \ V /  __/ | | (_| | (_| |  __/")
        logo.append(r"     \____/\___/ \_/ \___|_|  \__,_|\__, |\___|")
        logo.append(r"                                     __/ |")
        logo.append(r"                                    |___/")
        logo.append("")
        out.write("\n".join(logo))
        self.modules[-1][1][1] = len(self.sensors)
        all_uncovered = 0
        for mod in self.modules:
            lines, sensorlines, uncovered = self.check_on_covered(mod)
            all_uncovered+=len(uncovered)
            out.write("\n")
            out.write("-"*(len(mod[0])+14)+".\n")
            out.write(" Coverage : %s  |\n"%mod[0])
            out.write("-"*(len(mod[0])+14)+"'\n")
            import math
            n = int(math.ceil(math.log(len(lines),10)))
            out.write("0"*n+"\n")
            if show_sensor:
                sensor_mark = "s"
            else:
                sensor_mark = ""
            for i,l in enumerate(lines):
                l = l.rstrip()
                if i+1 in sensorlines:
                    if i+1 in uncovered:
                        out.write("%%0%dd %%s  ==>  %%s\n"%n%(i+1,sensor_mark,l))
                    else:
                        out.write("%%0%dd %%s       %%s\n"%n%(i+1,sensor_mark,l))
                else:
                    out.write("%%0%dd         %%s\n"%n%(i+1,l))
            begin, end = mod[1]
            k = end - begin
            created       = "  %d sensors created"%k
            if len(uncovered) == 0:
                not_responded =  "  all sensors responded"
            elif len(uncovered) == 1:
                not_responded = "  1 sensor did not respond"
            else:
                not_responded = "  %s sensors did not respond"%len(uncovered)
            len_f = len(mod[0])
            write_status()
        if len(self.modules)>1:
            write_resume()


class Sensor:
    def __init__(self, suite_begin, suite_end, **kwd):
        self.done        = False
        self.suite_begin = suite_begin
        self.suite_end   = suite_end
        Monitor().sensors.append(self)



