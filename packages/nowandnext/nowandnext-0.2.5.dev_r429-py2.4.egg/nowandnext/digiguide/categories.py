STRCATS = """Adult Entertainment
 Animation
 Arts
 Business and Finance
 Chat Show
 Childrens
 Comedy
 Consumer
 Cookery
 DIY
 Documentary
 Drama
 Education
 Entertainment
 Fashion
 Film
 Game Show
 Gardening
 Health
 History Documentary
 Kids Drama
 Magazine Programme
 Motoring
 Music
 Nature
 News
 Political
 Quiz Show
 Reality Show
 Religious
 Science Fiction Series
 Scientific Documentary
 Series
 Sitcom
 Soap
 Special Interest
 Sport
 Talk Show
 Technology
 Travel"""
 
CATEGORIES = [ a.strip().upper() for a in STRCATS.split("\n") ]
 
if __name__ == "__main__":
     import pprint
     pprint.pprint (CATEGORIES)