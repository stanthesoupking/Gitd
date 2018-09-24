from .entity import Entity


class Repository:
    '''Repository class, keeps track of entities that need updating'''

    def __init__(self, root: Entity, entities=[]):
        '''Object Initialiser  
        Args:
            root (Entity): Root entity of the repository
            entities ([]): Entity list to initialise the repository with
        '''
        self.root = root
        self.entities = entities

    def sync(self):
        '''Sync repository entities with their attached entities  
        Returns:
            bool: True if the repository synced without any errors, otherwise False.
        '''
        pass
