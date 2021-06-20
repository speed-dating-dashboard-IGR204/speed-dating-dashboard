

id2study = {
    1: 'Law',
    2: 'Math',
    3: 'Social Science, Psychologist' ,
    4: 'Medical Science, Pharmaceuticals, and Bio Tech',
    5: 'Engineering',
    6: 'English/Creative Writing/ Journalism',
    7: 'History/Religion/Philosophy',
    8: 'Business/Econ/Finance',
    9: 'Education, Academia',
    10: 'Biological Sciences/Chemistry/Physics',
    11: 'Social Work',
    12: 'Undergrad/undecided',
    13: 'Political Science/International Affairs',
    14: 'Film',
    15: 'Fine Arts/Arts Administration',
    16: 'Languages',
    17: 'Architecture',
    18: 'Other'
}

id2race = {
    1: 'Black/African American',
    2: 'European/Caucasian-American',
    3: 'Latino/Hispanic American',
    4: 'Asian/Pacific Islander/Asian-American',
    5: 'Native American',
    6: 'Other'
}

id2gender = {
    0: "Female",
    1: "Male"
}

id2goal = {
    1: "Seemed like a fun night out",
    2: "To meet new people",
    3: "To get a date",
    4: "Looking for a serious relationship",
    5: "To say I did it",
    6: "Other"
}

hobbies = ["sports","tvsports","exercise","dining","museums","art","hiking","gaming","clubbing","reading","tv","theater","movies","concerts","music","shopping","yoga"]


# Need a sort of trivial dictionary that just returns the key it was asked for
class KeyDict(dict):
    def __missing__(self, key):
        return key


id2id = KeyDict()

# A dictionary that links the column name with the appropriate conversion dictionary
id2label_dict = {
    "field_cd": id2study,
    "race": id2race,
    "gender": id2gender,
    "goal": id2goal
}
