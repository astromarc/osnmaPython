import logging


logging.basicConfig(filename="logname.log",
                    filemode='a',
                    format='%(asctime)s.%(msecs)d;%(levelname)s;%(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Received page 2 from SV3")
logging.info("Page Completed for SV3")
logging.info("SV3 self-authenticated")
logging.warning("SV4 cannot be cross-authenticated by SV3")

22:34:38.657,WARNING, Hello Jamet!