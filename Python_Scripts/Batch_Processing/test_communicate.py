import subprocess
import logging

log_file = "log_file.log"
## Setting Up Logger:
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename=log_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d (%H:%M:%S)')
handler.setFormatter(formatter)
log.addHandler(handler)


log.info("The Process Starts Here" + "\n")

command = "ls " + "-lhap"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = process.communicate()[0]

log.info("Writing Output to Log File" + "\n")
log.info(output.decode("utf-8") + "\n")
log.info("Finished Writing Output")


log.info("\n" + "The Process is Now Finished")

'''
with open("test.txt", "w") as output_file:
    output_file.write(output.decode("utf-8"))
'''


