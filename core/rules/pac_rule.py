

class PacRule():
    """PAC rules define for tech
    """
    def __init__(self, tech_name, min_width, min_space, expand=True):
        self.tech_name = tech_name
        self.min_width = min_width
        self.min_space = min_space
        self.expand = expand
    