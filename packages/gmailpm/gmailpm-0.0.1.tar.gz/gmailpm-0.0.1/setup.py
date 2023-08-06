from distutils.core import setup
setup(
    name = "gmailpm",
    packages = ["gmailpm"],
    version = "0.0.1",
    description = "Project Monitoring based on GMail",
    author = "Wolfgang Lechner",
    author_email = "wolfgang.lechner@gmail.com",
    url = "",
    download_url = "",
    keywords = ["project", "monitoring", "scientific","gmail"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering"
        ],
    long_description = """\
    gmailpm allows you to monitor the progress of extended jobs using gmail.
    
    Usage:
    1. Create a TGmailProjectMonitoring object

       import gmailpm as gpm
       pm = gpm.TGmailProjectMonitoring(emailAddress="youremailaddress@gmail.com", emailPassword="yourpassword",projectName="TestProject")

       Note, that the class TGmailProjectMonitoring requires 3 arguments, your emailaddress, your password and a discription of the job.
       
            
    2. At the beginning of your code send a Mail to your gmail account with senStaretedMessage
       
       pm.sendStartedMessage()

       sendStartedMessage without arguments sends a message with the projectname as subject and hostname and current directory as body. You can
       override the body text with the optional argument info (eg. pm.sendStartedMessage(info="started\nat CLUSTER:./mydir") )
       
    3. In order to protocoll your progress you can send a progress message with
    
       pm.sendProgressMessage("After %d Steps: Avg=123456.7890" % (i,))


    Example:
    if __name__=="__main__":
        project = "TestProject"
        pm = TGmailProjectMonitoring(emailAddress="test.test@gmail.com",emailPassword="password",projectName=project)
        pm.sendStartedMessage(info="startedat CLUSTER:./mydir")
        pm.sendProgressMessage("Progress 50%")
        pm.sendProgressMessage("Finished")
    """
)
