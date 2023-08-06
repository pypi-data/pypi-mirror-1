---------------------------------------------------------------------------------
GMail Project Monitoring (gmailpm)

by
Dr. Wolfgang Lechner
wolfgang.lechner@gmail.com
---------------------------------------------------------------------------------

GmailPM is a small library that allows you to monitor your applications via gmail. 
Instead of actively checking the viability of your running jobs, you can let your
jobs send you status and progress as emails.
This might be interesting if you are running several long simulations on different
clusters. 



    Usage:
    1. Create a TGmailProjectMonitoring object

       import gmailpm.gmailpm as gpm
       pm = gpm.TGmailProjectMonitoring(emailAddress="youremailaddress@gmail.com",
                                        emailPassword="yourpassword",
                                       projectName="TestProject")

       Note, that the class TGmailProjectMonitoring requires 3 arguments, your 
       emailaddress, your password and a discription of the job.
       
            
    2. At the beginning of your code send a Mail to your gmail account with 
       senStaretedMessage
       
       pm.sendStartMessage()

       sendStartMessage without arguments sends a message with the projectname as
       subject and hostname and current directory as body. You can override the
       body text with the optional argument info:
       (eg. pm.sendStartMessage(info="started\nat CLUSTER:./mydir") )
       
    3. In order to protocoll your progress you can send a progress message with
    
       pm.sendProgressMessage("After %d Steps: Avg=123456.7890" % (i,))


    Example:
    if __name__=="__main__":
        project = "TestProject"
        pm = TGmailProjectMonitoring(emailAddress="test.test@gmail.com",
                                     emailPassword="password",
                                     projectName=project)
        pm.sendStartMessage(info="startedat CLUSTER:./mydir")
        pm.sendProgressMessage("Progress 50%")
        pm.sendProgressMessage("Finished")
    