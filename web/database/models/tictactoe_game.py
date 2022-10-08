from ..client import mongoEngine
import datetime

class TictactoeGame(mongoEngine.Document):
    meta = {"collection": "tictactoe_game"} # Collection name
    user = mongoEngine.ReferenceField("User", required=True)
    first_turn = mongoEngine.FloatField(required=True)
    created_at = mongoEngine.DateTimeField()
    updated_at = mongoEngine.DateTimeField(default=datetime.datetime.now)
    deleted_at = mongoEngine.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(TictactoeGame, self).save(*args, **kwargs)
    
    def update(self, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().update(**kwargs)