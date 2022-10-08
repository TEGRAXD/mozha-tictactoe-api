from ..client import mongoEngine
import datetime

class TictactoeMove(mongoEngine.Document):
    meta = {"collection": "tictactoe_move"} # Collection name
    user = mongoEngine.ReferenceField("User")
    game = mongoEngine.ReferenceField("TictactoeGame", required=True)
    turn = mongoEngine.IntField(required=True)
    turn_monitor = mongoEngine.FloatField(required=True)
    move = mongoEngine.ListField(mongoEngine.IntField(), required=True)
    board = mongoEngine.ListField(mongoEngine.ListField(mongoEngine.FloatField()), required=True)
    status = mongoEngine.IntField(required=True)
    created_at = mongoEngine.DateTimeField()
    updated_at = mongoEngine.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(TictactoeMove, self).save(*args, **kwargs)
    
    def update(self, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().update(**kwargs)