import requests

def getPage (url: str):
    try:
        res = requests.get(url=url)
        return res.text 
    except Exception as e:
        raise Exception('Getting page failed: ' + url) from e

def main():
    try:
        print(getPage('https://jobs.ashbyhq.com/linqapp/a80957d5-94b1-4be4-9d1b-f396ec3b36eb?utm_source=5W61yBO2K0'))
    except Exception as e:
        print(e.args)
    

if __name__ == '__main__':
    main()