from grun import grun
import time


def processer_with_text():
        for i in range(0,10):
            yield float(i)/10, "Step %d" % i
            time.sleep(0.01)

def processer_without_text():
        for i in range(0,10):
            yield float(i)/10
            time.sleep(0.01)


grun( processer_with_text() )
grun( processer_without_text() )
grun( processer_without_text(), name="I've got a NEW name" )



