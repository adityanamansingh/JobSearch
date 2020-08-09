import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict
from collections import Counter
import re


class JobPost:
    def __init__(self, title: str, location: str, company: str, description: str):
        self.title = title
        self.location = location
        self.company = company
        self.description = description
        # No ID attribute to improve scalability, Indeed.com uses IDs, but other job posting sites may not

    def wordCounts(self):
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
                entry = entry[1:-1] + re.sub('[^A-Za-z0-9\+\-\#]', '', entry[-1]) + re.sub('[^A-Za-z0-9]', '', entry[0])
                entry = entry.lower()
                wordCounts[entry] += 1
            return wordCounts



class JobSearch:
    # Initializes the JobSearch with a list of locations, positions OPTIONAL: job type and radius
    def __init__(self, positionList : List[int], locationList : List[int], jobType: str=None , rad: int=None):

        self.positionList = [str] * len(positionList)
        for i, jobTitle in enumerate(positionList):
            # Formats input for use in a search
            self.positionList[i] = jobTitle.replace(" ", "+")

        self.locationList = [str] * len(locationList)
        for i, location in enumerate(locationList):
            # Formats input for use in a search
            self.locationList[i] = location.replace(" ", "+")

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

        indeedURLs = self._makeIndeedURLs()

        resultCount = 0
        self.indeedJobIsSeen = set()

        for URL in indeedURLs:
            # Builds a list of jobs for a set family of URLs
            jobPostings = self._getJobPosts(URL)
            for job in jobPostings:
                # Loading in console
                resultCount += 1
                print(' . ', end='')
                if resultCount % 20 == 0:
                    print()

                jobID = job["id"][2:]
                # If we have not seen the job before, parse the JobPost
                if jobID not in self.indeedJobIsSeen:
                    self.indeedJobIsSeen.add(jobID)

                    """               
                    Parses a single indeed job and returns JobPost object
                    jobPost could be stored as a class attribute in a list of JobPost Objects for future reference
                    if needed
                    """
                    jobPost = self._parseIndeedJob(job, jobID)

                    if jobPost is not None:
                        jobWordCounter = jobPost.wordCounts()

                        self.JSBlacklist = []
                        blacklisted = False
                        for word in self.JSBlacklist:
                            if word in jobWordCounter:
                                blacklisted = True

                        # If the job description contains a blacklisted word, the words in its descriptions are not
                        # not counted
                        if not blacklisted:
                            self.wordCounter += jobWordCounter
        print('\n', "Count:", resultCount)

    """
    Returns a list of pairs of the most frequently used words in the job descriptions related to the specified
    locations and positions.
    
    List contents are limited by displayCount, if there is no limit specified (-1), wordFrequency will return all words 
    and their frequency
    
    Outline of indeed.com searches:
    https://www.indeed.com/jobs?q=jobTitle&l=location&radius=rad&jt=jobType
    Base Search (Only job and location listed):
    https://www.indeed.com/jobs?q=jobTitle&l=location
    Basic + Job Type:
    https://www.indeed.com/jobs?q=jobTitle&l=Location&jt=jobType
    This is a URL for a basic indeed job search, specifying the 4 variables, jobTitle, location, rad, and jobType
    All variables are strings formatted such that spaces become "+" signs
    
    Example:
    San Jose, CA = San+Jose,+CA
    
    jobTitle and location variables can be any string; however, rad and jobType are limited in their choices
    rad: 5, 10, 15, 25, 50, 100
    jobType: internship, fulltime, parttime, temporary, contract
    """
    # Intended for internal use to modularize code
    def _parseIndeedJob(self, job: "bs4.elements.Tag", jobID: str) -> JobPost:
        # Each job will have their information stored in the tags and classes listed below
        # job is a Tag object in the BS4 library, with an attribute "id", which is the unique specifier for each job
        # Each "id" is a CSS selector to allow for organization of different elements in the design
        # First two characters "p_" from id attribute are stripped to allow for appending into URL
        jobTitle = job.find("a", class_="jobtitle")
        jobCompany = job.find("span", class_="company")
        jobLocation = job.find('span', class_="location")

        # job is a Tag object in the BS4 library, with an attribute "id", which is the unique specifier for each job
        # Each "id" is a CSS selector to allow for organization of different elements in the design
        # First two characters "p_" from id attribute are stripped to allow for appending into URL

        indeedJobURL = f"https://www.indeed.com/viewjob?jk={jobID}"
        indeedJobHTML = requests.get(indeedJobURL)
        indeedJobSoup = BeautifulSoup(indeedJobHTML.content, "html.parser")
        jobDescription = indeedJobSoup.find("div", id="jobDescriptionText")

        if None in [jobTitle, jobCompany, jobLocation, jobDescription]:
            return None

        return JobPost(jobTitle.text.strip(), jobCompany.text.strip(), jobLocation.text.strip(), jobDescription.text)

    def _makeIndeedURLs(self):
        indeedURLs = []
        if self.rad is None and self.jobType is None:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}")
        elif self.jobType is None:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&radius={self.rad}")
        elif self.rad is None:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&jt={self.jobType}")
        else:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURLs.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&radius={self.rad}&jt={self.jobType}")

        return indeedURLs

    def _getJobPosts(self, URL: str) -> List["bs.elements.Tag"]:
        jobPostings = []
        # returns entire HTML text for given URL
        indeedJSHTML = requests.get(URL)
        # Creates a BeautifulSoup object for HTML parsing with the 'html.parser' in the Python library
        indeedJSSoup = BeautifulSoup(indeedJSHTML.content, "html.parser")
        jobCount = int(indeedJSSoup.find("div", id="searchCountPages").text.strip().split()[3])
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

    def getWordFrequency(self, displayCount: int = 0, blacklist: List[str] = []) -> List[Tuple[str, int]]:
        frequencyCounts = Counter()
        if displayCount < 1:
            for key, value in self.wordCounter.most_common():
                if key not in blacklist:
                    frequencyCounts[key] = value
            return frequencyCounts.most_common()

        for key, value in self.wordCounter.most_common(displayCount):
            if key not in blacklist:
                frequencyCounts[key] = value
        return frequencyCounts.most_common()

    def getWord(self, word: List[str]) -> int:
        return self.wordCounter[word.lower()]
    """
    resumeWeights is a txt document listing key words and relative weights
    
    Example:
    intern internship 1.0 # If intern or internship are found, the relative weight is applied, does not double count
    
    vs
    
    Example:
    intern internship 1.0 # If it is a fall internship, it will receive additional weight
    fall . 5
    
    """
    def companyFit(self, resumeWeights: str) -> List[Tuple[str, float]]:
        pass


js = JobSearch(["Software Engineer Intern", "Software Developer Intern"], ["San Francisco, CA", "San Jose, CA", "Long Beach, CA"], "internship")
js.getWordFrequency()
counts = js.wordCounter
print(counts)
print("C++:", js.getWord("python"))