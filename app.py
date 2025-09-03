from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional
import requests

Base = declarative_base()

class Cat(Base):
    __tablename__ = 'cats'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    experience = Column(Integer)
    breed = Column(String)
    salary = Column(Float)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=True)

class Mission(Base):
    __tablename__ = 'missions'
    id = Column(Integer, primary_key=True)
    complete = Column(Boolean, default=False)

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)
    notes = Column(String, default="")
    complete = Column(Boolean, default=False)
    mission_id = Column(Integer, ForeignKey('missions.id'))

Cat.mission = relationship("Mission", back_populates="cat", foreign_keys=[Cat.mission_id], uselist=False)
Mission.cat = relationship("Cat", back_populates="mission", uselist=False)
Mission.targets = relationship("Target", back_populates="mission")
Target.mission = relationship("Mission", back_populates="targets")

# sqlite
engine = create_engine('sqlite:///spy.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#pdm
class CatCreate(BaseModel):
    name: str
    experience: int
    breed: str
    salary: float

class CatUpdate(BaseModel):
    salary: float

class CatResponse(BaseModel):
    id: int
    name: str
    experience: int
    breed: str
    salary: float
    mission_id: Optional[int]

    #pyst
    class Config:
        from_attributes = True

class TargetCreate(BaseModel):
    name: str
    country: str

class TargetNotesUpdate(BaseModel):
    notes: str

class TargetResponse(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    complete: bool

    class Config:
        from_attributes = True  # For Pydantic v2

class MissionCreate(BaseModel):
    targets: List[TargetCreate]

class MissionResponse(BaseModel):
    id: int
    complete: bool
    cat_id: Optional[int] = None  # Default to None for unassigned missions
    targets: List[TargetResponse]

    class Config:
        from_attributes = True  # For Pydantic v2
        arbitrary_types_allowed = True

    @classmethod
    def from_orm(cls, obj):
        # Map cat_id from the cat relationship
        return cls(
            id=obj.id,
            complete=obj.complete,
            cat_id=obj.cat.id if obj.cat else None,
            targets=[TargetResponse.from_orm(t) for t in obj.targets]
        )

class AssignCat(BaseModel):
    cat_id: int

def validate_breed(breed: str):
    """
    Breed validation by CatApi
        """
    try:
        response = requests.get("https://api.thecatapi.com/v1/breeds")
        response.raise_for_status()
        breeds = [b['name'] for b in response.json()]
        if breed not in breeds:
            raise HTTPException(status_code=400, detail="Invalid breed")
    except:
        raise HTTPException(status_code=500, detail="Breed validation failed")

@app.post("/cats", response_model=CatResponse)
def create_cat(cat: CatCreate, db: Session = Depends(get_db)):
    validate_breed(cat.breed)
    #validate+create
    db_cat = Cat(name=cat.name, experience=cat.experience, breed=cat.breed, salary=cat.salary)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/cats", response_model=List[CatResponse])
def list_cats(db: Session = Depends(get_db)):
    """
    List all cats
        """
    return db.query(Cat).all()

@app.get("/cats/{cat_id}", response_model=CatResponse)
def get_cat(cat_id: int, db: Session = Depends(get_db)):
    """
    get 1 cat
        """
    cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat

@app.put("/cats/{cat_id}", response_model=CatResponse)
def update_cat(cat_id: int, update: CatUpdate, db: Session = Depends(get_db)):
    """
    new salary
        """
    cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    cat.salary = update.salary
    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    """
        delete 1 cat if it hasn't mission
            """
    cat = db.query(Cat).filter(Cat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    if cat.mission_id:
        raise HTTPException(status_code=400, detail="Cannot delete cat with active mission")
    db.delete(cat)
    db.commit()
    return {"ok": True}

@app.post("/missions", response_model=MissionResponse)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    """
        new mission+targets
            """
    # range 1-3
    if not 1 <= len(mission.targets) <= 3:
        raise HTTPException(status_code=400, detail="Targets must be between 1 and 3")
    db_mission = Mission()
    db.add(db_mission)
    db.flush()
    for target in mission.targets:
        db_target = Target(mission_id=db_mission.id, name=target.name, country=target.country)
        db.add(db_target)
    db.commit()
    db.refresh(db_mission)
    return MissionResponse.from_orm(db_mission)

@app.get("/missions", response_model=List[MissionResponse])
def list_missions(db: Session = Depends(get_db)):
    return [MissionResponse.from_orm(m) for m in db.query(Mission).all()]

@app.get("/missions/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    """
        1 mission
            """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse.from_orm(mission)

@app.delete("/missions/{mission_id}")
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    """
        delete mission if it is not active
            """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    # if active - false
    if mission.cat:
        raise HTTPException(status_code=400, detail="Cannot delete assigned mission")
    db.delete(mission)
    db.commit()
    return {"ok": True}

@app.patch("/missions/{mission_id}/assign")
def assign_cat(mission_id: int, assign: AssignCat, db: Session = Depends(get_db)):
    """
        assign cat if it has't mission
            """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.cat:
        raise HTTPException(status_code=400, detail="Mission already assigned")
    cat = db.query(Cat).filter(Cat.id == assign.cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    if cat.mission:
        raise HTTPException(status_code=400, detail="Cat already has a mission")
    mission.cat = cat
    cat.mission_id = mission_id
    db.commit()
    return {"ok": True}

# Update target notes
@app.patch("/missions/{mission_id}/targets/{target_id}/notes")
def update_target_notes(mission_id: int, target_id: int, update: TargetNotesUpdate, db: Session = Depends(get_db)):
    """
       update existing or add new note
            """
    target = db.query(Target).filter(Target.id == target_id, Target.mission_id == mission_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    mission = target.mission
    if target.complete or mission.complete:
        raise HTTPException(status_code=400, detail="Cannot update notes for completed target or mission")
    target.notes = update.notes
    db.commit()
    return {"ok": True}

# Mark target as complete
@app.patch("/missions/{mission_id}/targets/{target_id}/complete")
def complete_target(mission_id: int, target_id: int, db: Session = Depends(get_db)):
    """
       end one target + mission complete check
            """
    target = db.query(Target).filter(Target.id == target_id, Target.mission_id == mission_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    mission = target.mission
    if target.complete:
        raise HTTPException(status_code=400, detail="Target already completed")
    if mission.complete:
        raise HTTPException(status_code=400, detail="Mission already completed")
    target.complete = True
    db.commit()
    if all(t.complete for t in mission.targets):
        mission.complete = True
        # IMP If targets complete - mission too
        if mission.cat:
            mission.cat.mission_id = None
            mission.cat = None
        db.commit()
    return {"ok": True}