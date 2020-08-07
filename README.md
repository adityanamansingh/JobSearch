# JobSearchWordCloud
  Intended to scrape job description information from websites such as: Indeed, Monster, etc. and analyze input in order to identify potential "buzzwords" that should be utilized in resume writing.

 ## Indeed.com HTML Inspection
  Upon inspecting Indeed.com, I see that the job search elements in the left column each have a specific ID, in this picture, the job "Software Engineering Internship" at Apple, the ID is "p_6f4667b07ff6b946". In order to access the full job description, the URL appends the previous search parameters "software%20engineering%20%intern" and "San%20Jose%20%2C%20CA" with the string "&vjk=6f4667b07ff6b946". Further inspection reveals that all other job postings follow the same format with the first two characters being "p_", str[2:] can be used to format the ID for appending onto search results.

  N job titles in M locations with c results (depending on the pair of job titles and locations) will determine how many different URLs are visited and how many jobs may be parsed. Duplicate jobs (traced through their unique ID) will not be parsed. In total, there will be N * M * (c_avg) jobs parsed.

![Alt Text](/jobsearch/IndeedJSHTML2.png?raw=true)

  Other important information to parse is contained within the job description, each full job description is only accessible through the unique ID, the URL "https://www.indeed.com/viewjob?jk=6f4667b07ff6b946" allows for a more easily parsable HTML design. As you can see below, the job decription is contained within the <div> "jobDescriptionText"

![Alt Text](/jobsearch/IndeedJSHTML3.png?raw=true)

  Lastly, accessing the different pages of the job search must be accounted for as well. As you can see below, at the top of the page it states "Page 4 of 74 jobs." Each page contains 15 job postings, and as oddly as it is formatted, the results are not actually 74 pages worth, rather 4 pages of 15 and a 5th page of 14. The URL oddly says "&start=30" for the 4th page, but given that each subsequent page contains 15 jobs, it should actually start at 45.

![Alt Text](/jobsearch/IndeedJSHTML1.png?raw=true)

  I intend to use a few different job titles while analyzing the job searches: "Software Engineering Intern", "Software Engineering Internship", "Software Developer Intern", "Software Developer Internship", "Software Intern", "Software Internship", "Computer Science Intern", "Computer Science Internship". Of course replacing "intern" with "internship" is probably overkill, but I am attempting to leverage as large of a data set as possible. I have also compiled a list of the major tech cities in America, because regardless of location, the skills in demand should be relatively the same for an intern. The cities I have compiled include: "San Jose, CA", "San Francisco, CA", "Seattle, WA", "Austin, TX", "Boston, MA", "Chicago, IL", "Denver, CO", "Los Angeles, CA", "New York City, NY" among others. Places nearby like Mountain View, Cupertino, Palo Alto, Redmond are typically included in the 25 mile radius searches; however, the ability to adjust radius to greater than 25 is implemented as well.

  In all, 8 job titles in 9 cities, averaging around 50-100 results each search, will produce 3600 - 7200 different job descriptions to be parsed. Each job having somewhere in the ball park of 250 words, will amount to around 900,000 - 1.8 million words analyzed and utilized to define the most desireable traits and skills in software development for interns.

## JobSearch Object Processing
  Job descriptions will be saved in a txt document upon creation of a **JobSearch** object. Processing the job description information will require:
  - Checking for duplicates
      - If a job ID has not been seen, it is a new job and should be saved and analyzed
          1. Insertion and element indexing are O(1) with a set and it does not allow duplicates by nature of design. A set will hold all job ID values
  - Analyzing and Saving
      - Writing data to a txt file is straight forward, and to aid in processing in the future, text should be formatted to allow for easy parsing.
          1. Each entry should begin with a line solely dedicated to job ID (This format may change in the future to allow for unique identification between websites)
          2. The next portion of lines should simply be the text from the job description
          3. There should also be a way to signify that a job entry is complete
      - The job descriptions must be parsed if they are not duplicates, ensuring that a count of all instances of a word are recorded
          1. On the other hand, a hash map or the subclass "Counter" in Python is better suited to track instances of words (O(1) as well). Considering that I am not concerned with case sensitivity, all words shall be entered in lowercase format to ensure that words like "Software" and "software" add to the same count. I could either operate on the first character of every word for slightly better performance, or I could ensure that the entire word was lowercase to improve the accuracy of the data. <sup>1</sup>

## Word Cloud Creation
  The word cloud will be created very simply. It will consist of X number of most frequently seen words and font size will reflect relative usage. The word cloud text will *fit* into different shapes with differing fonts and text colors. I will either implement with JavaFX or experiment with a Python GUI framework.

<sup>1</sup>: In Python, a "Counter" is a container that works exactly like a dictionary (hash map) except values represent occurances or "counts." Using the indexing operator will return a 0 if the element is not contained within the container rather than a KeyError while using a dictionary. This is beneficial if you wanted to see how many times a word is mentioned.
