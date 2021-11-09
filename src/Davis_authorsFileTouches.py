import json
import requests
import csv


# GitHub Authentication function
def github_auth(url, lsttoken, ct):
    jsonData = None
    try:
        ct = ct % len(lstTokens)
        headers = {'Authorization': 'Bearer {}'.format(lsttoken[ct])}
        request = requests.get(url, headers=headers)
        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        pass
        print(e)
    return jsonData, ct


# @dictFiles, empty dictionary of files
# @lstTokens, GitHub authentication tokens
# @repo, GitHub repo
def countfiles(dictfiles, lsttokens, repo, authors, commDates):
    ipage = 1  # url page counter
    ct = 0  # token counter

    try:
        # loop though all the commit pages until the last returned empty page
        while True:
            spage = str(ipage)
            commitsUrl = 'https://api.github.com/repos/' + repo + '/commits?page=' + spage + '&per_page=100'
            jsonCommits, ct = github_auth(commitsUrl, lsttokens, ct)

            # break out of the while loop if there are no more commits in the pages
            if len(jsonCommits) == 0:
                break
            # iterate through the list of commits in  spage
            for shaObject in jsonCommits:
                sha = shaObject['sha']
                # For each commit, use the GitHub commit API to extract the files touched by the commit
                shaUrl = 'https://api.github.com/repos/' + repo + '/commits/' + sha
                shaDetails, ct = github_auth(shaUrl, lsttokens, ct)

                filesjson = shaDetails['files']

                # print(shaUrl)

                for filenameObj in filesjson:
                    filename = filenameObj['filename']

                    if filename.endswith('.java'):
                        author = shaDetails['commit']['author']['name']
                        commDate = shaDetails['commit']['author']['date']

                        dictfiles[filename] = dictfiles.get(filename, 0) + 1
                        authors.append(author)
                        commDates.append(commDate)

                        print(filename + " - " + author + " - " + commDate)

            ipage += 1
    except:
        print("Error receiving data")
        exit(0)


# GitHub repo
# repo = 'johnxu21/sre2020-21'
repo = 'scottyab/rootbeer'
# repo = 'Skyscanner/backpack'  # This repo is commit heavy. It takes long to finish executing
# repo = 'k9mail/k-9' # This repo is commit heavy. It takes long to finish executing
# repo = 'mendhak/gpslogger'


# put your tokens here
# Remember to empty the list when going to commit to GitHub.
# Otherwise they will all be reverted and you will have to re-create them
# I would advise to create more than one token for repos with heavy commits
lstTokens = ["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", "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"]


dictfiles = dict()
authors = []
commDates = []
counter = 0
countfiles(dictfiles, lstTokens, repo, authors, commDates)

print('Total number of files: ' + str(len(dictfiles)))

file = repo.split('/')[1]

# change this to the path of your file
fileOutput = 'data/file_' + file + '.csv'
rows = ["Filename", "Author", "Touches", "Date"]
fileCSV = open(fileOutput, 'w')
writer = csv.writer(fileCSV)
writer.writerow(rows)

bigcount = None
bigfilename = None

for filename, count in dictfiles.items():
    rows = [filename, count, authors[counter], commDates[counter]]
    writer.writerow(rows)
    if bigcount is None or count > bigcount:
        bigcount = count
        bigfilename = filename
fileCSV.close()
print('The file ' + bigfilename + ' has been touched ' + str(bigcount) + ' times.')
