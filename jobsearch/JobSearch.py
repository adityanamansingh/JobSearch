import requests
from bs4 import BeautifulSoup

from typing import List, Tuple


class JobSearch:
    """
    Initializes the JobSearch with a list of locations and positions
    """
    def __init__(self, locationList : List[int], positionList : List[int],  jobType: str=None , rad: int=None):
        self.locationList = [str] * len(locationList)
        for i, location in enumerate(locationList):
            self.locationList[i] = location.replace(" ", "+")

        self.positionList = [str] * len(positionList)
        for i, jobTitle in enumerate(positionList):
            self.positionList[i] = jobTitle.replace(" ", "+")

        # error handling for rad and jobType
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

        indeedURL = []
        if self.rad is None and self.jobType is None:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURL.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}")
        elif self.rad is None:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURL.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&jt={self.jobType}")
        else:
            for i, jobTitle in enumerate(self.positionList):
                for j, location in enumerate(self.locationList):
                    indeedURL.append(f"https://www.indeed.com/jobs?q={jobTitle}&l={location}&radius={self.rad}&jt={self.jobType}")

        r = requests.get(indeedURL[0])
        print(indeedURL[0])
        soup = BeautifulSoup(r.content, "html.parser")
        results = soup.find(id="resultsCol")
        print(results.prettify())
        # look for <td id="resultsCol">
        # nested is <a id="jobPostingsAnchor" tabindex="-1"></a> containing all jop postings
        # All jobs are contained like with class="jobsearch-SerpJobCard unifiedRow row result clickcard"
        # Each job has their own CSS selector which acts as a unique identifier
        #for URL in indeedURL:
            #r = requests.get(URL)
            #print(r.text)


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
    def wordFrequency(self, displayCount: int=-1) -> List[Tuple[str, int]]:
        pass

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


js = JobSearch(["San Francisco, CA", "San Jose, CA", "Long Beach, CA"], ["Software Engineer Intern", "Software Developer Intern"], "internship")
js.wordFrequency()