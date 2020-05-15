friends_scan_list = [ 
                "All",
                "Following",
                "Followers",
                "Work",
                "College",
                "Current City",
                "Hometown",
            ]
friends_section = [
                "/friends",
                "/following",
                "/followers",
                "/friends_work",
                "/friends_college",
                "/friends_current_city",
                "/friends_hometown",
            ]
friends_elements_path = [
                "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                "//*[contains(@class,'_3i9')][1]/div/div/ul/li[1]/div[2]/div/div/div/div/div[2]/ul/li/div/a",
                "//*[contains(@class,'fbProfileBrowserListItem')]/div/a",
                "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            ]
friends_file_names = [
                "All Friends.txt",
                "Following.txt",
                "Followers.txt",
                "Work Friends.txt",
                "College Friends.txt",
                "Current City Friends.txt",
                "Hometown Friends.txt",
            ]

about_scan_list = [
                "Overview",
                "Education",
                "Living",
                "Contact-info",
                "Relationship",
                "Bio",
                "Year-overviews",
            ]

about_section = [
                "/about?section=overview",
                "/about?section=education",
                "/about?section=living",
                "/about?section=contact-info",
                "/about?section=relationship",
                "/about?section=bio",
                "/about?section=year-overviews",
            ]
about_elements_path = [
                "//*[contains(@id, 'pagelet_timeline_app_collection_')]/ul/li/div/div[2]/div/div"
            ] * 7
about_file_names = [
                "Overview.txt",
                "Work and Education.txt",
                "Places Lived.txt",
                "Contact and Basic Info.txt",
                "Family and Relationships.txt",
                "Details About.txt",
                "Life Events.txt",
            ]

posts_scan_list = ["Posts, comments and reactions"]
posts_section = []
posts_elements_path = ['//div[@class="_5pcb _4b0l _2q8l"]']

posts_file_names = ["Posts.txt"]

def choose(ids, *elements):
    ret_elements = []
    for element in elements:
        tmp = []
        for i in ids:
            tmp.append(element[i])
        ret_elements.append(tmp)
    return ret_elements
if __name__ == "__main__":
    choose([1, 2], friends_section, friends_elements_path)