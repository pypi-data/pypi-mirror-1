'''

TGmailProjectMonitoring allows users to monitor extended processes.
Instead of actively checking the progress of these jobs the I propose
a strategy, where your applications send the information to you. 

by Wolfgang Lechner (wolfgang.lechner@gmail.com)

'''
import smtplib
import email.Utils
import os

class TGmailProjectMonitoring(object):
    '''
    Usage:
    1. Create a TGmailProjectMonitoring object

       import gmailpm.gmailpm as gpm
       pm = gpm.TGmailProjectMonitoring(emailAddress="youremailaddress@gmail.com", emailPassword="yourpassword",projectName="TestProject")

       Note, that the class TGmailProjectMonitoring requires 3 arguments, your emailaddress, your password and a discription of the job.
       
            
    2. At the beginning of your code send a Mail to your gmail account with senStaretedMessage
       
       pm.sendStartMessage()

       sendStartMessage without arguments sends a message with the projectname as subject and hostname and current directory as body. You can
       override the body text with the optional argument info (eg. pm.sendStartMessage(info="started\nat CLUSTER:./mydir") )
       
    3. In order to protocoll your progress you can send a progress message with
    
       pm.sendProgressMessage("After %d Steps: Avg=123456.7890" % (i,))


    Example:
    import gmailpm.gmailpm as gpm
    if __name__=="__main__":
        project = "TestProject"
        pm = gpm.TGmailProjectMonitoring(emailAddress="test.test@gmail.com",emailPassword="password",projectName=project)
        pm.sendStartMessage(info="startedat CLUSTER:./mydir")
        pm.sendProgressMessage("Progress 50%")
        pm.sendProgressMessage("Finished")
    '''
    
    def __init__(self,emailAddress,emailPassword,projectName):
        '''
        Email Adress and Password are necessary to login at gmail
        projectName is used as Subject
        '''
        self._emailAddress  = emailAddress
        self._emailPassword = emailPassword
        self._projectName = projectName
        self._replymsgid = 'NOTSET'
        
    
    def _sendMessage(self,emaildata):
        """
        Sends emaildata via the smptlib.sendmail function
        """
        connection = smtplib.SMTP("smtp.gmail.com",587)
        connection.ehlo()
        connection.starttls()
        connection.login(self._emailAddress, self._emailPassword)
        connection.sendmail(self._emailAddress, self._emailAddress, emaildata)
        connection.close()
    
    def _getComputerInfo(self):
        """
        returns Hostname and current directory
        """
        return str(os.getenv('HOSTNAME')) + " at " + os.getcwd()
    
    def sendStartMessage(self,info='',tag='projectmonitoring'):
        """
        Sends a Message that the job started and saves the msgid in order to
        be able to reply to this message
        """
        if not(info):
            info = self._getComputerInfo()
        else:
            info.rstrip('\n')+'\n'
        msgid = email.Utils.make_msgid()
        msgdict = [['To:'          , self._emailAddress.replace('@','+'+tag+'@')],
                   ['From:'        , self._emailAddress],
                   ['Message-ID:'  , msgid],
                   ['Subject:'     , str(self._projectName)]
                   ]
        emaildata = "\n".join(["%s %s" % (k,v) for k,v in msgdict]) + "\n" + str(info) + "\n\n"
        self._sendMessage(emaildata)
        self._replymsgid = msgid
    
    def sendProgressMessage(self,report,tag='projectmonitoring'):
        """
        Sends a progress report
        """
        msgid = email.Utils.make_msgid()
        if self._replymsgid == "NOTSET":
            raise Exception("Use sendStartMessage() first")
        else:
            msgdict = [['MIME-Version:' , "1.0"],
                       ['In-Reply-To:'  , self._replymsgid],
                       ['References:'   , self._replymsgid],
                       ['To:'           , self._emailAddress.replace('@','+'+tag+'@')],
                       ['From:'         , self._emailAddress.replace('@','+'+tag+'@')],
                       ['Message-ID:'   , msgid],
                       ['Subject:'      , "Re: "+ str(self._projectName)]
                      ]
            emaildata = "\n".join(["%s %s" % (k,v) for k,v in msgdict]) + "\n" + str(report) + "\n\n"
            self._sendMessage(emaildata)
    
        
if __name__=="__main__":
    print TGmailProjectMonitoring.__doc__

    
    
        
