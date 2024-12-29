import random
import statistics
import matplotlib.pyplot as plt

class AgeGroup:
    A_25_34 = 2
    A_35_44 = 3
    A_45_54 = 4
    A_55_64 = 5
    A_65_74 = 6
    A_75 = 7

class Gender:
    MALE = 0
    FEMALE = 1

class Area:
    URBAN = 0
    SEMI_URBAN = 1
    RURAL = 2

class Education:
    PRIMARY = 0
    HS = 1
    BACHELOR = 2
    VT = 3
    MASTER = 4

class Assign:
    def calculate_by_distribution(self, dist:dict):
        """
        Selects categories based on pre-defined probability distributions
        """
        target = random.uniform(0, 1)
        stack = 0
        for attr, dist in dist.items():
            stack += dist
            if stack >= target:
                return attr

    def age(self) -> int: # Assign an age based on the below distribution
        distribution = {
            AgeGroup.A_25_34: 0.12,
            AgeGroup.A_35_44: 0.14,
            AgeGroup.A_45_54: 0.16,
            AgeGroup.A_55_64: 0.18,
            AgeGroup.A_65_74: 0.20,
            AgeGroup.A_75: 0.20
        }
        return self.calculate_by_distribution(distribution)

    def gender(self) -> Gender: # Assign a gender based on the below distribution
        # 48.5% Male :: 51.5% Female
        return [Gender.MALE, Gender.FEMALE][random.uniform(0, 1)>=0.485]
    
    def area(self) -> Area: # Assign an area based on the below distribution
        distribution = {
            Area.URBAN: 0.5,
            Area.SEMI_URBAN: 0.3,
            Area.RURAL: 0.2
        }
        return self.calculate_by_distribution(distribution)
    
    def education(self) -> Education: # Assign an education based on the below distribution
        distribution = {
            Education.PRIMARY: 0.02,
            Education.HS: 0.48,
            Education.VT: 0.2,
            Education.BACHELOR: 0.2,
            Education.MASTER: 0.1,
        }
        return self.calculate_by_distribution(distribution)

    def attachment(self, agent:'Agent', base_clamp:tuple=(0.1, 0.6)) -> tuple[float]:
        '''
        Calculates an attachment value from 0 to 1, through two steps.
        First, each agent is assigned a random value between 0.1 and 0.6.
        Second, each of the following features give an additional 0.1:
        female, older than 44, rural dweller, master's degree.
        '''

        orig = value = random.uniform(*base_clamp)

        if agent.age > AgeGroup.A_35_44:
            value += 0.1

        if agent.gender == Gender.FEMALE:
            value += 0.1

        if agent.education == Education.MASTER:
            value += 0.1

        if agent.area == Area.RURAL:
            value += 0.1

        assert 0 <= value <= 1 # Ensure this attachment value does not exceed 1
        return round(orig, 2), round(value, 2)
        # Return the original random value as well, to see how his traits affect his attachment

class Agent:
    def __init__(self):
        """
        Generates a random agent on initialisation
        """
        assign = Assign()
        self.age = assign.age()
        self.gender = assign.gender()
        self.area = assign.area()
        self.education = assign.education()
        self.orig_attachment, self.attachment = assign.attachment(self)

    def hardcode(self, age:AgeGroup, gender:Gender, area:Area, education:Education, attachment:float=None):
        """
        Allows a hard-coded agent to be created. Attachment parameter is optional.
        One can experiment with different traits and observe how the calculated
        attachment level varies depending on the values chosen for the various traits.
        """
        assign = Assign()
        self.age = age
        self.gender = gender
        self.area = area
        self.education = education
        self.orig_attachment, self.attachment = (-1.0, attachment) if attachment else assign.attachment()

    def format(self):
        """
        Creates a formatted string of the
        agent to visualize its traits.
        """
        age_format = {
            AgeGroup.A_25_34: '25-34',
            AgeGroup.A_35_44: '35-44',
            AgeGroup.A_45_54: '45-54',
            AgeGroup.A_55_64: '55-64',
            AgeGroup.A_65_74: '65-74',
            AgeGroup.A_75: '75+'
        }

        gender_format = {
            Gender.MALE: 'Male',
            Gender.FEMALE: 'Female'
        }

        area_format = {
            Area.URBAN: 'Urban',
            Area.SEMI_URBAN: 'Semi-Rural',
            Area.RURAL: 'Rural'
        }

        education_format = {
            Education.PRIMARY: 'Primary',
            Education.HS: 'High-school',
            Education.VT: 'Vocational Training',
            Education.BACHELOR: 'Bachelor',
            Education.MASTER: 'Master',
        }

        age = age_format.get(self.age)
        gender = gender_format.get(self.gender)
        area = area_format.get(self.area)
        education = education_format.get(self.education)

        return f'{age} :: {gender} :: {area} :: {education} :: {self.attachment} :: {self.orig_attachment}'


def interact_opinion(agent:'Agent', _agent:'Agent', constant=0.05):
    """
    This interaction makes it harder for extreme opinions
    to be changed. An attachment value close to 0.5 will
    be more easily influenced than one at 0.1 or 0.9.
    """

    a_influence = (0.5-abs(0.5-agent.attachment))/0.5 * constant
    _a_influence = (0.5-abs(0.5-_agent.attachment))/0.5 * constant

    if agent.attachment > _agent.attachment:
        agent.attachment -= a_influence
        _agent.attachment += _a_influence
    else:
        agent.attachment += a_influence
        _agent.attachment -= _a_influence

def get_shared_traits(agent:'Agent', _agent:'Agent', traits=['age', 'gender', 'area', 'education']):
    '''
    Return the number of shared traits between two agents
    '''
    return sum([getattr(agent, attr) == getattr(_agent, attr) for attr in traits])


def probability_interaction_shared(agent:'Agent', _agent:'Agent', total_traits=4):
    '''
    Calculates the probability of an interaction between
    two agents based on the similarity of their traits.
    '''
    return get_shared_traits(agent, _agent) / total_traits

class Community:
    def __init__(self, size:int=100):
        """
        Generates a community of {size} agents
        """
        self.agents:list[Agent] = []
        for _ in range(size):
            self.agents.append(Agent())


    def interact(self, iterations:int=1, interaction_function=interact_opinion):
        """
        Makes the agents interact between them.
        """

        random.shuffle(self.agents)

        complete = []
        while len(self.agents) > 1:
            agent = self.agents.pop()
            _agent = self.agents.pop()

            if random.uniform(0, 1) < probability_interaction_shared(agent, _agent):
                interaction_function(agent, _agent)
                agent.attachment = round(agent.attachment, 2)
                _agent.attachment = round(_agent.attachment, 2)

            complete += [agent, _agent]
        self.agents = complete

        if iterations > 0:
            self.interact(iterations-1, interaction_function)

    def attachment_list(self, gender=None, area=None):
        if area:
            return [agent.attachment for agent in self.agents if agent.area == area]
        if gender:
            return [agent.attachment for agent in self.agents if agent.gender == gender]
        return [agent.attachment for agent in self.agents]

    def get_average_attachment(self, gender=None, area=None):
        return statistics.mean(self.attachment_list(gender, area))


community = Community(1000)
avrg = [community.get_average_attachment()]

for k in range(250):
    community.interact(interaction_function=interact_opinion)
    avrg.append(community.get_average_attachment())

plt.figure()
plt.plot(avrg, color='red')

plt.xlabel('Number of interactions')
plt.ylabel('Average attachment level')

plt.show()
