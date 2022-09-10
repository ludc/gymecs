

class Asset:
    def build_visual_np(self):
        raise NotImplementedError
    
    def build_bullet_np(self):
        raise NotImplementedError

    def build_entity(self):
        raise NotImplementedError