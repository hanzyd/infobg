
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

region_municipality = Table(
    "region_municipality",
    Base.metadata,
    Column("region_code", Integer, ForeignKey("region.code")),
    Column("municipality_code", Integer, ForeignKey("municipality.code")),
)

municipality_town = Table(
    "municipality_town",
    Base.metadata,
    Column("municipality_code", Integer, ForeignKey("municipality.code")),
    Column("town_code", Integer, ForeignKey("town.code")),
)

town_institution = Table(
    "town_institution",
    Base.metadata,
    Column("town_code", Integer, ForeignKey("town.code")),
    Column("institution_code", Integer, ForeignKey("institution.code")),
)

class Region(Base):
    __tablename__ = "region"
    code = Column(Integer, primary_key=True)
    name = Column(String)
    municipalities = relationship("Municipality", backref=backref("region"))

class Municipality(Base):
    __tablename__ = "municipality"
    code = Column(Integer, primary_key=True)
    name = Column(String)
    towns = relationship("Town", backref=backref("municipality"))

class Town(Base):
    __tablename__ = "town"
    code = Column(Integer, primary_key=True)
    name = Column(String)
    institutions = relationship("Institution", backref=backref("town"))

class Financing(Base):
    __tablename__ = "financing"
    code = Column(Integer, primary_key=True)
    label = Column(String)

class InstitutionDetails(Base):
    __tablename__ = "details"
    code = Column(Integer, primary_key=True)
    label = Column(String)

class InstitutionState(Base):
    __tablename__ = "state"
    code = Column(Integer, primary_key=True)
    label = Column(String)

class Institution(Base):
    __tablename__ = "institution"
    code = Column(Integer, primary_key=True)
    name = Column(String)
    region = Column(Integer, ForeignKey("region.code"))
    municipality = Column(Integer, ForeignKey("municipality.code"))
    town = Column(Integer, ForeignKey("town.code"))
    details = Column(Integer, ForeignKey("details.code"))
    financing = Column(Integer, ForeignKey("financing.code"))
    state = Column(Integer, ForeignKey("state.code"))

class TownPopulation(Base):
    __tablename__ = "town_population"
    index = Column(Integer, primary_key=True)
    year = Column(Date)
    town = Column(Integer, ForeignKey("town.code"))
    permanent = Column(Integer)
    current = Column(Integer)

class StateSubjectExams(Base):
    __tablename__ = "state_subject_exams"
    label = Column(String, primary_key=True)

class StateExams(Base):
    __tablename__ = "state_exams"
    index = Column(Integer, primary_key=True)
    institution = Column(Integer, ForeignKey("institution.code"))
    date = Column(Date)
    score = Column(Numeric)
    students = Column(Integer)
    subject = Column(Integer, ForeignKey("state_subject_exams.label"))

class ExternalEvaluation(Base):
    __tablename__ = "external_evaluation"
    index = Column(Integer, primary_key=True)
    institution = Column(Integer, ForeignKey("institution.code"))
    date = Column(Date)
    bel_score = Column(Numeric)
    bel_students = Column(Integer)
    math_score = Column(Numeric)
    math_students = Column(Integer)
