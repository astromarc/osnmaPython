from rich.live import Live
from rich.text import Text
from rich.table import Table
from datetime import datetime
import csv


class updateLogs:
    """
    This is a simple Rich Class used to show the last Logs stored in the CSV Class
    The number of rows shown is configurable by using the "numRows" parameter
    """
    def __init__(self,logFile,numRows):
        self.__logFile = logFile
        self.__numRows = numRows
    def __rich__(self) -> Table:
        table3 = Table()
        table3.add_column("Date and Time")
        table3.add_column("Category")
        table3.add_column("Message")
        with open(self.__logFile, 'r') as csvfile:
            csvreader = list(csv.reader(csvfile))
            for row in csvreader[-self.__numRows:]:
                try:
                    if row[1] == "WARNING":
                        text66 = Text("WARNING")
                        text66.stylize(style="bold white on yellow")
                        table3.add_row(row[0], text66, row[2])
                    if row[1] == "ERROR":
                        text66 = Text("ERROR")
                        text66.stylize(style="bold white on red")
                        table3.add_row(row[0], text66, row[2])
                    if row[1] == "INFO":
                        text66 = Text("INFO")
                        text66.stylize(style="bold white on green")
                        table3.add_row(row[0], text66, row[2])
                except: pass
        return table3
    
class Clock:
    """Renders the time in the center of the screen."""
    def __rich__(self) -> Text:
        return Text("OSNMA live Demonstrator v0  "+datetime.now().ctime(), style="bold magenta", justify="center")

class DSM_Info():
    def __init__(self):
        self.__NMAS = "Unknown"
        self.__DSMBlocks = "Unknown"
        self.__DSMBlocksTotal = "Unkmown"
        self.__DSMId = "Unkmown"
        self.__HKROOT = "Unkmown"
        self.__HKROOTTime = "Unkmown"
        self.__HKROOTVerificationStatus = "True"
        self.__chainID = "Unkmown"
        self.__chainID = "Unkmown"
        self.__chainStatus = "Unkmown"
        self.__teslaKey  = "Unknown"
        self.__teslaKeyStatus  = "Unknown"
    def __rich__(self) -> Text:
            textOsnmaStatus = Text("OSNMA Status: ")
            textCurrentDSMID = Text ("Current DSM ID: ")
            textCurrentBlocks = Text ("Current DSM Blocks: ")
            textKRTOOTKey = Text ("Current HKRoot: ")
            textKRTOOTKeyTime = Text ("Current HKRoot Date: ")
            textKRTOOTVerificationStatus = Text ("Current HKRoot is verified: ")
            textChainID = Text ("Last Chain ID: ")
            textChainStatus = Text ("Last Chain Status: ")
            textTeslaKey = Text ("Last Tesla Key:")
            textTeslaKeyStatus = Text ("Last Tesla Key belongs to chain:")
            
            textOsnmaStatus.stylize("bold")
            textCurrentDSMID.stylize("bold")
            textCurrentBlocks.stylize("bold")
            textKRTOOTKey.stylize("bold")
            textKRTOOTKeyTime.stylize("bold")
            textChainID.stylize("bold")
            textTeslaKey.stylize("bold")
            textChainStatus.stylize("bold")
            textKRTOOTVerificationStatus.stylize("bold")
            textTeslaKeyStatus.stylize("bold")
            
            NMAS = self.colourNMAS()
            teslaKeyStatusColour = self.colourTeslaKey()
            rootKeyStatusColour = self.colourRootKey()
            
            DSMInfoUpdated = Text(justify="right")
            DSMInfoUpdated =  textOsnmaStatus + NMAS + "\n" + textCurrentDSMID + Text(
                        str(self.__DSMId)+"\n") + textCurrentBlocks + Text(
                        str(self.__DSMBlocks)+" / "+ str(self.__DSMBlocksTotal),
                        ) + "\n" + textKRTOOTKey + str(self.__HKROOT) + "\n" + textKRTOOTKeyTime + str(self.__HKROOTTime) + "\n" +textKRTOOTVerificationStatus + rootKeyStatusColour +"\n" + textChainID + str(self.__chainID) + " \n"+ textChainStatus + str(self.__chainStatus) +"\n" + textTeslaKey + str(self.__teslaKey)+"\n" + textTeslaKeyStatus + teslaKeyStatusColour
                        
            return DSMInfoUpdated
    def updateParameters(self, NMAS, DSMId, DSMBlocks, DSMTotal, ChainId, ChainStatus, TeslaKey, hkroot, hkrootTime,hkrootverification, teslaStatus):
        self.__NMAS = NMAS
        self.__DSMId = DSMId
        self.__DSMBlocks = DSMBlocks
        self.__DSMBlocksTotal = DSMTotal
        self.__chainID = ChainId
        self.__chainStatus = ChainStatus
        self.__teslaKey = TeslaKey
        self.__HKROOT = hkroot
        self.__HKROOTTime = hkrootTime
        self.__HKROOTVerificationStatus = hkrootverification
        self.__teslaKeyStatus = teslaStatus
    def colourNMAS(self):
        NMASColour = Text(str(self.__NMAS))
        if self.__NMAS == "Test":
            NMASColour.stylize("Black on  Yellow")
        else:
            NMASColour.stylize("White on Red")
        if self.__NMAS == "Operational":
            NMASColour.stylize("White on Green")
        return NMASColour
    def colourTeslaKey(self):
        TeslaStatusColour = Text(str(self.__teslaKeyStatus))
        if self.__teslaKeyStatus == True:
            TeslaStatusColour.stylize("White on Green")
        else:
            TeslaStatusColour.stylize("White on Red")
        return TeslaStatusColour

    def colourRootKey(self):
        RootStatusColour = Text(str(self.__HKROOTVerificationStatus))
        if self.__HKROOTVerificationStatus == True:
            RootStatusColour.stylize("White on Green")
        else:
            RootStatusColour.stylize("White on Red")
        return RootStatusColour

class svTable:
    def __init__(self):
        self.__tableSV = Table(title="Space Vehicles",show_header=False, show_lines=True)
        self.__tableSV.add_row("SV1","SV2","SV3","SV4","SV5","SV6","SV7","SV8","SV9", )
        self.__tableSV.add_row("SV10","SV11","SV12","SV13","SV14","SV15","SV16","SV17","SV18",)
        self.__tableSV.add_row("SV19","SV20","SV21","SV22","SV23","SV24","SV25","SV26","SV27",)
        self.__tableSV.add_row("SV28","SV29","SV30","SV31","SV32","SV33","SV34","SV35","SV36",)
    def __rich__(self) -> Text:
        table = self.getTable()
        return table
    def updateParameters(self,constellation):
        numSv =  constellation.getSvNum()
        numRows = 4
        self.__tableSV = Table(title="Space Vehicles",show_header=False, show_lines=True)

        svFirstRow = [Text() for i in range(int(numSv/numRows))]
        svSecondRow = [Text() for i in range(int(numSv/numRows))]
        svThirdRow = [Text() for i in range(int(numSv/numRows))]
        svFourthRow = [Text() for i in range(int(numSv/numRows))]
        
        for i in range(int(numSv/numRows)):
            
            index = 0
            progressInt = int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100)
            progress = Text(str(int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100))+"%")
            progress = self.getProgressStyle(progressInt, progress)
            osnmaSelfStatus = constellation.getSvSelfAuthenticationStatus(i+1+index*int(numSv/numRows))
            osnmaCrossStatus = constellation.getSvCrossAuthenticationStatus(i+1+int(index*numSv/numRows))
            svCrossStatus = ""
            if not any(item is  None for item in osnmaCrossStatus):
                svCrossStatus = self.getCrossAuthenticationStyle(i+1+int(index*numSv/numRows), osnmaCrossStatus)
            svSelfStatus = self.getSelfAuthenticationStyle(i+1+index*int(numSv/numRows),osnmaSelfStatus)
            
            svFirstRow[i] = svSelfStatus+"\n"+svCrossStatus+progress
            
            
            index = 1
            progressInt = int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100)
            progress = Text(str(int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100))+"%")
            progress = self.getProgressStyle(progressInt, progress)
            osnmaSelfStatus = constellation.getSvSelfAuthenticationStatus(i+1+index*int(numSv/numRows))
            svSelfStatus = self.getSelfAuthenticationStyle(i+1+index*int(numSv/numRows),osnmaSelfStatus)
            osnmaCrossStatus = constellation.getSvCrossAuthenticationStatus(i+1+int(index*numSv/numRows))
            svCrossStatus = ""
            if not any(item is  None for item in osnmaCrossStatus):
                svCrossStatus = self.getCrossAuthenticationStyle(i+1+int(index*numSv/numRows), osnmaCrossStatus)
            svSecondRow[i] = svSelfStatus+"\n"+svCrossStatus+progress
            
            index = 2
            progressInt = int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100)
            progress = Text(str(int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100))+"%")
            progress = self.getProgressStyle(progressInt, progress)
            osnmaSelfStatus = constellation.getSvSelfAuthenticationStatus(i+1+index*int(numSv/numRows))
            svSelfStatus = self.getSelfAuthenticationStyle(i+1+index*int(numSv/numRows),osnmaSelfStatus)
            osnmaCrossStatus = constellation.getSvCrossAuthenticationStatus(i+1+int(index*numSv/numRows))
            svCrossStatus = ""
            if not any(item is  None for item in osnmaCrossStatus):
                svCrossStatus = self.getCrossAuthenticationStyle(i+1+int(index*numSv/numRows), osnmaCrossStatus)
            svThirdRow[i] =svSelfStatus+"\n"+svCrossStatus+progress

            index = 3
            progressInt = int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100)
            progress = Text(str(int(constellation.getSVSubFrameProgress(i+1+int(index*numSv/numRows))*100))+"%")
            progress = self.getProgressStyle(progressInt, progress)
            osnmaSelfStatus = constellation.getSvSelfAuthenticationStatus(i+1+index*int(numSv/numRows))
            svSelfStatus = self.getSelfAuthenticationStyle(i+1+index*int(numSv/numRows),osnmaSelfStatus)
            osnmaCrossStatus = constellation.getSvCrossAuthenticationStatus(i+1+int(index*numSv/numRows))
            svCrossStatus = ""
            if not any(item is  None for item in osnmaCrossStatus):
                svCrossStatus = self.getCrossAuthenticationStyle(i+1+int(index*numSv/numRows), osnmaCrossStatus)
            svFourthRow[i] =svSelfStatus+"\n"+svCrossStatus+progress


        self.__tableSV.add_row(*svFirstRow)
        self.__tableSV.add_row(*svSecondRow)
        self.__tableSV.add_row(*svThirdRow)
        self.__tableSV.add_row(*svFourthRow)
        
    def getCrossAuthenticationStyle(self,svId,status):
        sv = Text("")
        if status[0] is not None:
            sv = sv + Text("[SV"+str(status[0])+"]")
            if status[1] == 0:
                sv.stylize("white on green")
            if status[1] == 1:
                sv.stylize("white on red")
            if status[1] == 2:
                sv.stylize("black on yellow")
            sv = sv + Text("\n")
        return sv
    
    def getTable(self):
        return self.__tableSV
    def getProgressStyle(self,progressInt,progress):
        if 0 < progressInt < 50:
            progress.stylize("black on Yellow")
        if 50 <= progressInt < 100:
            progress.stylize("underline black on Yellow")
        if progressInt == 100: progress.stylize("white on green")
        return progress
    
    def getSelfAuthenticationStyle(self,svId,status):
        sv = Text("SV"+str(svId))
        if status == 0:
            sv.stylize("white on green")
        if status == 1:
            sv.stylize("white on red")
        if status == 2:
            sv.stylize("black on yellow")
        if status == None:
            return sv
        return sv