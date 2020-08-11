# JobSearchWordCloud
Intended to scrape job description information from websites such as: Indeed, Monster, etc. and analyze input in order to identify potential "buzzwords" that should be utilized in resume writing.

## JobSearch Object
Used to scrape information from job posting websites: Job titles, locations, companies, and descriptions
Attributes:
- positionList: list of str specifying the positions you are seeking
- locationList: : list of str specifying the locations you would be willing to work
- jobType: optional parameter that can specify the kind of job you are looking for
- rad: optional parameter that can specify how far from your desired locations you'd like to work
- wordCounter: Counter object with every word that has been seen within a job search
- resultsCounts: The number of unique jobs parsed

Methods:
- __init__(self, positionList: List[str], locationList: List[str], jobType: str = None, rad: int = None)
    1. Purpose: 
        - preparing a JobSearch object for analysis, parses through all jobs related to specified search parameters additional functionality for a job description blacklist is already prepared if a user would like to toss a job description from parsing if it contained certain blacklisted words
    2. Parameters:
        - positionList: list of str specifying the positions you are seeking
        - locationList: list of str specifying the locations you would be willing to work
        - jobType: optional parameter that can specify the kind of job you are looking for
            1. The current functionality of the JobSearch object is for Indeed.com with the following job types: fulltime, parttime, internship, temporary, and contract
        - rad: optional parameter that can specify how far from your desired locations you'd like to work
            1. Additional functionality to allow for a Tuple[str, int] could be allowed instead of simply a List[str] for locationList to allow a user to specify a radius from a distinct city
    3. Other Attributes:
        - wordCounter: Counter object with every word that has been seen within a job search
        - resultsCount: The number of unique jobs parsed
- getWordFrequency(self, displayCount: int = 0, blacklist: List[str] = None) -> Counter
    1. Purpose: 
        - Returns a Counter object that specifies how many instances of (displayCount) words have been seen. Allows for a blacklist to be passed to suppress certain words from being displayed. For instance, if the user did not want to see results for the word "Java", they could specify such in the blacklist.
    2. Parameters:
        - displayCount: int specifying how many of the most commonly seen words to display, if displayCount is < 1, all results are displayed
        - blacklist: list of str specifying words to omit from results shown
- getWord(self, word: str) -> int
    1. Purpose: 
        - Returns the amount of times an instance of the specified word is seen
    2. Parameters:
        - word: str that specifies which word you would like to examine for instances in the job search
        
## JobPostObject
Used to store information about a job. Added capability to parse through job description for word frequencies
Attributes:
- title: str specifying the title of the job post
- location: str specifying the location of the job
- company: str specifying the company offering the job
- description: str describing the respective job position

Methods:
- __init__(self, title: str = "", location: str = "", company: str = "", description: str = "")
    1. Purpose:
        - Passing parameters into class attributes
    2. Parameters:
        - title: str specifying the title of the job post
        - location: str specifying the location of the job
        - company: str specifying the company offering the job
        - description: str describing the respective job position
- wordCounts(self) -> Counter
    1. Purpose:
        - Builds a Counter object that tracks the frequency that words are used
# Results
After parsing through 2213 software engineering focused internships across the United States, I saw some interesting trends.
Here are a few of the most frequently used words that could help in a tech interns resume:
<center>

---| Useful Words In A Tech Resume |---
:-:|:-:|:-:
Amazon: 1099 | Teams: 1078 | Java: 727
Microsoft: 690 | Creative: 673 | AWS: 612
C++: 587 | Communications: 534 | Cloud: 519
Hardware: 510 | Passion: 483 | Object-Oriented: 472
Python: 459 | Scale: 454 | Analytics 436
Reliability: 434 | Analytical: 421 | Passionate: 412
Collaborative: 407 | Database: 407 | C#: 401
Independently: 393 | Flexible: 381 | Fast-paced: 380
Communicate: 369 | Positive: 369 | Bachelor's: 368
Dyanamic: 357 | Collaboration: 354 | Interpersonal: 331
Facebook: 361 | Scaling: 316 | Algorithms: 299
Motivated: 275 | Driven: 240 | Linux: 231
JavaScript: 222 | AI: 219 | Initiative: 208
Reliable: 208 | Efficiency: 200 | Problem-solving: 194
Efficient: 187 | Google: 187 | Embedded: 185
Networks: 185 | Paypal: 181 | Statistics: 171
    
</center>

It is important to note that these words are taken out of context, where a lot of their meaning is ultimately derived; however, I hope this information is useful in seeing some of the things tech recruiters or ATS might be looking for (generally) in a resume belonging to a potential intern. I found it interesting how **Amazon** ended up being the first tech/behavior related word, and was worlds above the next mentioned company, **Facebook**, at **361 instances**, over **700 instances below Amazon's**. I'd be curious to see how many of the job postings belong to Amazon and how many times Amazon is referenced *outside* of Amazon job postings. It's also important to note that **AWS**, an Amazon service, is referenced **612 times**, which again, is very high on the list, **"cloud"** is also a related term.

The **behavioral trait** most often referenced was **"creative"** followed by **"communications"** (which could be interpretted to mean any number of things), and finally **"passion."** The most often referenced programming languages, in order: **Java: 727**, **C++: 587**, **Python: 459**, **C#: 401** and **JavaScript: 222**.

Overall, it was an interesting dive into the metrics behind what recuiters might be looking for. I don't think I will be name dropping Amazon or Facebook anytime soon, but I now have some solid guidelines behind how I should build my resume and my skills moving forward. Please feel free to ask me questions or try it out for yourself, even if you aren't looking for an internship, or even majoring in tech, you may find some interesting trends!

# How it was designed

## Indeed.com HTML Inspection
  Upon inspecting Indeed.com, I see that the job search elements in the left column each have a specific ID, in this picture, the job "Software Engineering Internship" at Apple, the ID is "p_6f4667b07ff6b946". In order to access the full job description, the URL appends the previous search parameters "software%20engineering%20%intern" and "San%20Jose%20%2C%20CA" with the string "&vjk=6f4667b07ff6b946". Further inspection reveals that all other job postings follow the same format with the first two characters being "p_", str[2:] can be used to format the ID for appending onto search results.

  N job titles in M locations with c results (depending on the pair of job titles and locations) will determine how many different URLs are visited and how many jobs may be parsed. Duplicate jobs (traced through their unique ID) will not be parsed. In total, there will be N * M * (c_avg) jobs parsed.

<center>
    ![Alt Text](/jobsearch/IndeedJSHTML2.png?raw=true)
</center>

  Other important information to parse is contained within the job description, each full job description is only accessible through the unique ID, the URL "https://www.indeed.com/viewjob?jk=6f4667b07ff6b946" allows for a more easily parsable HTML design. As you can see below, the job description is contained within the <div> "jobDescriptionText"

<center>
    ![Alt Text](/jobsearch/IndeedJSHTML3.png?raw=true)
</center

  Lastly, accessing the different pages of the job search must be accounted for as well. As you can see below, at the top of the page it states "Page 4 of 74 jobs." Each page contains 15 job postings, and as oddly as it is formatted, the results are not actually 74 pages worth, rather 4 pages of 15 and a 5th page of 14. The URL oddly says "&start=30" for the 4th page, but given that each subsequent page contains 15 jobs, it should actually start at 45.
  
<center>
    ![Alt Text](/jobsearch/IndeedJSHTML1.png?raw=true)
</center>

  I intend to use a few different job titles while analyzing the job searches: "Software Engineering Intern", "Software Engineering Internship", "Software Developer Intern", "Software Developer Internship", "Software Intern", "Software Internship", "Computer Science Intern", "Computer Science Internship". Of course replacing "intern" with "internship" is probably overkill, but I am attempting to leverage as large of a data set as possible. I have also compiled a list of the major tech cities in America, because regardless of location, the skills in demand should be relatively the same for an intern. The cities I have compiled include: "San Jose, CA", "San Francisco, CA", "Seattle, WA", "Austin, TX", "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "New York City, NY" among others. Places nearby like Mountain View, Cupertino, Palo Alto, Redmond are typically included in the 25 mile radius searches; however, the ability to adjust radius to greater than 25 is implemented as well.

  In all, 8 job titles in 9 cities, averaging around 50-100 results each search, will produce 3600 - 7200 different job descriptions to be parsed. Each job having somewhere in the ball park of 250 words, will amount to around 900,000 - 1.8 million words analyzed and utilized to define the most desireable traits and skills in software development for interns.

