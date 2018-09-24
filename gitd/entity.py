from enum import Enum


class EntityType(Enum):
    '''Entity type'''
    FOLDER = 1
    FILE = 2


class Entity:
    '''Base Entity class'''

    def __init__(self, name: str, type: EntityType):
        '''Object Initialiser  
        Args:
            name (str): Name of the entity
            type (EntityType): Type of entity
        '''
        self.name = name
        self.type = EntityType
        self.attached_to = None

    def __eq__(self, other: Entity):
        '''Check this entity's content is equal to another entity by comparing  
        MD5 checksums.  
        Args:
            other (Entity): Entity to compare to

        Returns:
            True if both entity MD5's are equal, otherwise, return False.
        '''
        # Get MD5 Checksums
        md5_self = self.get_md5_checksum()
        md5_other = other.get_md5_checksum()

        # Return true if they are equal
        return md5_self == md5_other

    def get_md5_checksum(self):
        '''Get the MD5 Checksum of this entity  
        Returns:
            MD5 Checksum in string format
        '''
        raise NotImplementedError(
            "Subclasses of entity must implement MD5 Checksum getter")

    def get_modified_time(self):
        '''Get the modified time (seconds) since epoch of this entity  
        Returns:
            Entity modified time in seconds
        '''
        raise NotImplementedError(
            "Subclasses of entity must implement modified time getter")

    def sync(self):
        '''Syncs this entity with it's attached entity, if one exists.  
        Returns:
            True if the entity was synced successfuly, otherwise, return False.
        '''
        pass

    def newer_than(self, other: Entity):
        '''Get if this entity is newer than the given entity  
        Args:
            other (Entity): Entity to compare the modifification date with
        Returns:
            True if this entity is newer than the provided entity.
        '''
        time_self = self.get_modified_time()
        time_other = other.get_modified_time()

        return time_self > time_other

    def older_than(self, other: Entity):
        '''Get if this entity is older than the given entity  
        Args:
            other (Entity): Entity to compare the modifification date with
        Returns:
            True if this entity is older than the provided entity.
        '''
        time_self = self.get_modified_time()
        time_other = other.get_modified_time()

        return time_self < time_other

    def attach(self, entity: Entity):
        '''Attach this entity to another entity for syncing purposes  
        Args:
            entity (entity): Entity to attach 
        '''
        self.attached_to = entity
