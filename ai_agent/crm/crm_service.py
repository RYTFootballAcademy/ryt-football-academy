from .database import SessionLocal, Player, Parent, Fee, Trial, Tournament

def register_player(name: str, age: int, position: str, parent_id: int = None):
    db = SessionLocal()
    player = Player(name=name, age=age, position=position, parent_id=parent_id)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def register_parent(name: str, contact: str):
    db = SessionLocal()
    parent = Parent(name=name, contact=contact)
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent

def record_fee(player_id: int, amount: float, status: str, due_date: str):
    db = SessionLocal()
    fee = Fee(player_id=player_id, amount=amount, status=status, due_date=due_date)
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee

def record_trial(player_id: int, date: str, result: str = None):
    db = SessionLocal()
    trial = Trial(player_id=player_id, date=date, result=result)
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial

def create_tournament(name: str, start_date: str, end_date: str):
    db = SessionLocal()
    tournament = Tournament(name=name, start_date=start_date, end_date=end_date)
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament
