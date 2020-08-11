import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Any
from collections import Counter
import re
import textwrap


class JobPost:
    def __init__(self, title: str = "", location: str = "", company: str = "", description: str = ""):
        self.title = title
        self.location = location
        self.company = company
        self.description = description
        # No ID attribute to improve scalability, Indeed.com uses IDs, but other job posting sites may not

    def wordCounts(self) -> Counter:
        # Counter object created for every individual job description
        # Allows for blacklisting of words to discard job descriptions if they mention certain keywords
        wordCounts = Counter()
        if self.description is not None:
            for word in self.description.split():
                entry = word
                """                
                Regular expression used to remove all characters from the end of a word that are not
                A-Z, a-z, 0-9, +, -, or #
                This is done to allow words such as c++, c#, self-motivated, to be counted, but it also will
                remove trailing punctuation or any other special characters
                Example: "diligent," should not be counted, but "diligent" should
                The first character in a string is also checked in case of parenthesis
                """
                entry = re.sub('[^A-Za-z0-9]', '', entry[0]) + entry[1:-1] + re.sub('[^A-Za-z0-9\+\-\#]', '', entry[-1])
                entry = entry.lower()
                wordCounts[entry] += 1
            return wordCounts


class JobSearch:
    # Initializes the JobSearch with a list of locations, positions OPTIONAL: job type and radius
    def __init__(self, positionList: List[str], locationList: List[str], jobType: str = None, rad: int = None):

        self.positionList = positionList
        self.locationList = locationList

        # Error handling for rad and jobType
        """
        radii = [5, 15, 25, 50, 100]
        if rad not in radii:
        """
        self.rad = rad

        """
        jobs = ["internship", "fulltime", "parttime", "temporary", "contract"]
        if jobType not in jobs:
        """
        self.jobType = jobType
        self.wordCounter = Counter()
        # Parameter for blacklist functionality. If a blacklist was specified, it would have to be turned into lowercase
        # in order to help with word matching
        self.JSDescriptionBlacklist = []

        """
        Indeed.com Job Search Web Scraper
        Parses for: Job Title, Company, Location, and Job Description
        Utilizes a CSS selector system for uniquely identifying jobs locally within site
        """
        # local variable for storing the starting point of indeed searches
        indeedURLs = self._makeIndeedURLs()

        # To count the number of jobs parsed
        self.resultCount = 0
        self._indeedJobIsSeen = set()
        self.wordCounter += self._getIndeedWordFrequency(indeedURLs)


    """
    Intended for internal use to modularize code
    Examines a jobs HTML attributes and stores them in a JobPost object for further analysis
    """
    def _parseIndeedJob(self, jobHTML: "bs4.elements.Tag", jobID: str) -> JobPost:
        # Each job will have their information stored in the tags and classes listed below
        # job is a Tag object in the BS4 library, with an attribute "id", which is the unique specifier for each job
        # Each "id" is a CSS selector to allow for organization of different elements in the design
        # First two characters "p_" from id attribute are stripped to allow for appending into URL
        jobTitle = jobHTML.find("a", class_="jobtitle")
        jobCompany = jobHTML.find("span", class_="company")
        jobLocation = jobHTML.find('span', class_="location")

        # job is a Tag object in the BS4 library, with an attribute "id", which is the unique specifier for each job
        # Each "id" is a CSS selector to allow for organization of different elements in the design
        # First two characters "p_" from id attribute are stripped to allow for appending into URL

        indeedJobURL = f"https://www.indeed.com/viewjob?jk={jobID}"

        indeedJobHTML = requests.get(indeedJobURL)

        indeedJobSoup = BeautifulSoup(indeedJobHTML.content, "html.parser")
        jobDescription = indeedJobSoup.find("div", id="jobDescriptionText")

        if None in [jobTitle, jobCompany, jobLocation, jobDescription]:
            return JobPost()

        return JobPost(jobTitle.text.strip(), jobCompany.text.strip(), jobLocation.text.strip(), jobDescription.text)

    """
    Intended for internal use to modularize code
    Takes the positionList and locationList passed to the constructor of the JobSearch object and builds
    a list of URLs for indeed.com usage
    """
    def _makeIndeedURLs(self) -> List[str]:
        indeedPositionList = [str] * len(self.positionList)
        for i, jobTitle in enumerate(self.positionList):
            # Formats input for use in a search
            indeedPositionList[i] = jobTitle.replace(" ", "+")

        indeedLocationList = [str] * len(self.locationList)
        for i, location in enumerate(self.locationList):
            # Formats input for use in a search
            indeedLocationList[i] = location.replace(" ", "+")

        indeedURLs = []
        if self.rad is None and self.jobType is None:
            for jobTitle in indeedPositionList:
                for location in indeedLocationList:
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}")
        elif self.jobType is None:
            for jobTitle in indeedPositionList:
                for location in indeedLocationList:
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&radius={self.rad}")
        elif self.rad is None:
            for jobTitle in indeedPositionList:
                for location in indeedLocationList:
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&jt={self.jobType}")
        else:
            for jobTitle in indeedPositionList:
                for location in indeedLocationList:
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&radius={self.rad}&jt={self.jobType}")

        return indeedURLs

    """
    Intended for internal use to modularize code
    Returns a list of HTML tags corresponding to the Indeed.com search URL
    """
    def _getIndeedJobPosts(self, URL: str) -> List["bs.elements.Tag"]:
        jobPostings = []
        # returns entire HTML text for given URL

        indeedJSHTML = requests.get(URL)

        # Creates a BeautifulSoup object for HTML parsing with the 'html.parser' in the Python library
        indeedJSSoup = BeautifulSoup(indeedJSHTML.content, "html.parser")
        jobCount = int(indeedJSSoup.find("div", id="searchCountPages").text.strip().split()[3].replace(",", ""))
        # Each page has 15 jobs, jobCount // 15 returns the number of pages - 1 if jobCount % 15 != 0
        resultsPerPage = 15
        pages = int(jobCount) // resultsPerPage
        # If the jobCount is not divisible by 15, such as: 14, 16 etc, 1 additional page must be added
        if jobCount % resultsPerPage != 0:
            pages += 1

        # Search position is denoted by the formula (page - 1) * 10
        # It's incorrect, but it is Indeed.com's convention, &start=10 * n
        startNumber = 10
        for searchPosition in range(0, pages * startNumber, startNumber):
            # The first page doesn't have anything additional appended to it on indeed.com
            if searchPosition == 0:
                newURL = URL
            # Each subsequent page
            else:
                newURL = URL + f"&start={searchPosition}"

            indeedJSHTML = requests.get(newURL)

            indeedJSSoup = BeautifulSoup(indeedJSHTML.content, "html.parser")
            # Parses HTML text for resultsCol, or where the job results for the URL are found
            results = indeedJSSoup.find(id="resultsCol")
            # Returns a list of jobPostings for the specified URL
            jobPostings += results.find_all("div", class_="jobsearch-SerpJobCard")

        return jobPostings

    def _getIndeedWordFrequency(self, indeedURLs: List[str]) -> Counter:
        indeedWordCounter = Counter()
        for URL in indeedURLs:
            # Builds a list of HTML tags corresponding to individual jobs based on Indeed.com search parameters
            jobPostings = self._getIndeedJobPosts(URL)
            for jobHTML in jobPostings:

                jobID = jobHTML["id"][2:]
                # If we have not seen the job before, parse the JobPost
                if jobID not in self._indeedJobIsSeen:
                    self.resultCount += 1

                    # Loading in console
                    # self._loading()
                    self._indeedJobIsSeen.add(jobID)

                    """               
                    Parses a single indeed job and returns a JobPost object
                    jobPost could be stored as a class attribute in a list of JobPost Objects for future reference
                    if needed
                    """
                    jobPost = self._parseIndeedJob(jobHTML, jobID)

                    # Sometimes an HTML element will return as None if the element isn't found,
                    # leaving a job posting incomplete.
                    if jobPost is not None:
                        jobWordCounter = jobPost.wordCounts()

                        # This block of code is to handle job searching if a blacklist is included
                        blacklisted = False
                        for word in self.JSDescriptionBlacklist:
                            if word in jobWordCounter:
                                blacklisted = True
                                break

                        # If the job description contains a blacklisted word, the words in its descriptions are not
                        # counted
                        if not blacklisted:
                            indeedWordCounter += jobWordCounter
        return indeedWordCounter

    """
    Intended for internal use to modularize code
    Allows for visualization of job search progress, printing a " . " for each job parsed
    """
    def _loading(self):
        rowLength = 20
        print(' . ', end='')
        if self.resultCount % rowLength == 0:
            print()

    """
    Returns a list of pairs of the most frequently used words in the job descriptions related to the specified
    locations and positions.

    List contents are limited by displayCount, if there is no limit specified (-1), wordFrequency will return all words 
    and their frequency
    """
    def getWordFrequency(self, displayCount: int = 0, blacklist: List[str] = None) -> List[Tuple[Any, int]]:
        if blacklist is None:
            blacklist = []

        # Lowercasing the words to allow for proper hashing
        for i, word in blacklist:
            blacklist[i] = word.lower()

        if len(self.wordCounter) <= displayCount:
            return self.wordCounter.most_common()

        frequencyCounts = Counter()

        # Constructs a new Counter object with blacklisted words removed
        if displayCount < 1:
            for key, value in self.wordCounter.most_common():
                if key not in blacklist:
                    frequencyCounts[key] = value
            return frequencyCounts.most_common()

        displayed = 0
        for key, value in self.wordCounter.most_common():
            if key not in blacklist:
                frequencyCounts[key] = value
                displayed += 1
                if displayed == displayCount:
                    break

        return frequencyCounts.most_common()

    def getWord(self, word: str) -> int:
        return self.wordCounter[word.lower()]

    """
    resumeWeights is a txt document listing key words and relative weights
    
    Example:
    intern internship 1.0 # If intern or internship are found, the relative weight is applied, does not double count
    
    vs
    
    Example:
    intern internship 1.0 # If it is a fall internship, it will receive additional weight
    fall . 5
    
    Implementation is TBD
    """
    def companyFit(self, resumeWeights: str) -> List[Tuple[str, float]]:
        pass