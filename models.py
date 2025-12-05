#!/usr/bin/env python3

from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

from locations import Locations
from municipalities import Municipalities
from districts import Districts
from finance import Finances
from details import SchoolTypes
from subjects import Subjects
from scores import Scores
from transform import Transforms
from institutions import Institutions

Base = declarative_base()

district_municipality = Table(
    "district_municipality",
    Base.metadata,
    Column("district_abbrev", Integer, ForeignKey("district.abbrev")),
    Column("municipality_abbrev", Integer, ForeignKey("municipality.abbrev")),
)

municipality_settlement = Table(
    "municipality_settlement",
    Base.metadata,
    Column("municipality_abbrev", Integer, ForeignKey("municipality.abbrev")),
    Column("settlement_code", Integer, ForeignKey("settlement.code")),
)

settlement_institution = Table(
    "settlement_institution",
    Base.metadata,
    Column("settlement_code", Integer, ForeignKey("settlement.code")),
    Column("institution_code", Integer, ForeignKey("institution.code")),
)


# - Код на типа на териториалната единица:
#   1  "гр. "  -  град
#   3  "с.  "  -  село
#   7  "ман."  -  манастир
class SettlementType(Base):
    __tablename__ = "settlement_type"
    code = Column(Integer, primary_key=True)
    label = Column(String)

    def __repr__(self) -> str:
        return f"SettlementType({self.code!r}, {self.label!r})"


# - Надморска височина
#   Код  Групи (в метри)
#   1    до 49 вкл.
#   2    50 - 99 вкл.
#   3    100 - 199 вкл.
#   4    200 - 299 вкл.
#   5    300 - 499 вкл.
#   6    500 - 699 вкл.
#   7    700 - 999 вкл.
#   8    1000 и повече
class SettlementAltitude(Base):
    __tablename__ = "settlement_altitude"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"SettlementAltitude({self.code!r}, {self.label!r})"


class Settlement(Base):
    __tablename__ = "settlement"
    code = Column(String(5), primary_key=True)
    name = Column(String, nullable=False)
    municipality = Column(Integer, ForeignKey("municipality.abbrev"))
    kind = Column(Integer, ForeignKey('settlement_type.code'))
    altitude = Column(Integer, ForeignKey('settlement_altitude.code'))

    def __repr__(self) -> str:
        return f"Settlement({self.code!r}, {self.name!r})"


class Municipality(Base):
    __tablename__ = "municipality"
    abbrev = Column(String(5), primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"Municipality({self.abbrev!r}, {self.name!r})"


class District(Base):
    __tablename__ = "district"
    abbrev = Column(String(3), primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"District({self.abbrev!r}, {self.name!r})"


class InstitutionFinancing(Base):
    __tablename__ = "institution_financing"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"InstitutionFinancing({self.code!r}, {self.label!r})"


class InstitutionDetails(Base):
    __tablename__ = "institution_details"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"InstitutionDetails({self.code!r}, {self.label!r})"


class InstitutionState(Base):
    __tablename__ = "institution_state"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"InstitutionState({self.code!r}, {self.label!r})"


class Institution(Base):
    __tablename__ = "institution"
    code = Column(String(7), primary_key=True)
    name = Column(String, nullable=False)
    settlement = Column(String, ForeignKey("settlement.code"))
    details = Column(Integer, ForeignKey("institution_details.code"))
    financing = Column(Integer, ForeignKey("institution_financing.code"))
    state = Column(Integer, ForeignKey("institution_state.code"))

    def __repr__(self) -> str:
        return f"Institution({self.code!r}, {self.name!r})"


class SettlementPopulation(Base):
    __tablename__ = "settlement_population"
    year = Column(Date, primary_key=True)
    settlement = Column(String, ForeignKey("settlement.code"))
    permanent = Column(Integer, nullable=False)
    current = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"SettlementPopulation({self.year!r}, {self.settlement!r})"


class ExaminationSubject(Base):
    __tablename__ = "examination_subject"
    code = Column(Integer, primary_key=True)
    subject = Column(String, primary_key=True)

    def __repr__(self) -> str:
        return f"ExaminationSubject({self.code!r}, {self.subject!r})"


class Examination(Base):
    __tablename__ = "examination"
    index = Column(Integer, primary_key=True)
    institution = Column(Integer, ForeignKey("institution.code"))
    date = Column(Date)
    grade = Column(Integer)
    score = Column(Numeric)
    students = Column(Integer)
    subject = Column(Integer, ForeignKey("examination_subject.subject"))

    def __repr__(self) -> str:
        return f"Examination({self.institution!r}, {self.date!r})"


class Census(Base):
    __tablename__ = "census"
    index = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("settlement.code"))
    municipality = Column(String, ForeignKey("municipality.abbrev"))
    date = Column(Date)
    permanent = Column(Integer)
    current = Column(Integer)

    def __repr__(self) -> str:
        return f"Census({self.code!r}, {self.date!r})"


if __name__ == "__main__":
    engine = create_engine('sqlite:///models.sqlite')

    # Create all tables in the engine
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()

    e = [
        SettlementAltitude(code=1, label='до 49 вкл.'),
        SettlementAltitude(code=2, label='50 - 99 вкл.'),
        SettlementAltitude(code=3, label='100 - 199 вкл.'),

        SettlementType(code=1, label='гр.'),
        SettlementType(code=2, label='с.'),
        SettlementType(code=3, label='ман.'),
    ]

    session.add_all(e)
    session.commit()

    e = session.query(SettlementAltitude).filter_by(code=2).first()
    print(e)

    e = session.query(SettlementType).filter_by(label='с.').first()
    print(e)

    rows = []
    nodes = Locations()
    for n in nodes:
        rows.append(Settlement(code=n.code, name=n.name,
                               municipality=n.municipality,
                               kind=n.kind, altitude=n.altitude))
    session.add_all(rows)
    session.commit()

    e = session.query(Settlement).filter_by(code='29129').first()
    print(e)

    e = session.query(Settlement).filter_by(
        name='\u0422\u0443\u0442\u0440\u0430\u043a\u0430\u043d').first()
    print(e)

    rows = []
    nodes = Municipalities()
    for n in nodes:
        rows.append(Municipality(abbrev=n.abbrev, name=n.name))

    session.add_all(rows)
    session.commit()

    e = session.query(Municipality).filter_by(abbrev='BGS01').first()
    print(e)

    rows = []
    nodes = Districts()
    for n in nodes:
        rows.append(District(abbrev=n.abbrev, name=n.name))

    session.add_all(rows)
    session.commit()

    e = session.query(District).filter_by(abbrev='SHU').first()
    print(e)

    rows = []
    nodes = Finances()
    for n in nodes:
        rows.append(InstitutionFinancing(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionFinancing).filter_by(label='Духовно').first()
    print(e)

    rows = []
    nodes = Transforms()
    for n in nodes:
        rows.append(InstitutionState(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionState).filter_by(code=3).first()
    print(e)

    rows = []
    nodes = Institutions()
    for n in nodes:
        rows.append(Institution(code=n.id, name=n.name, settlement=n.location,
                                details=n.details, financing=n.finance,
                                state=n.status))
    session.add_all(rows)
    session.commit()

    rows = session.query(Institution).filter_by(code='103503').all()
    for r in rows:
        print(r)

    rows = []
    nodes = SchoolTypes()
    for n in nodes:
        rows.append(InstitutionDetails(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionDetails).filter_by(label='обединено').first()
    print(e)

    rows = []
    nodes = Subjects()
    for n in nodes:
        rows.append(ExaminationSubject(code=n.code, subject=n.title))

    session.add_all(rows)
    session.commit()

    e = session.query(ExaminationSubject).filter_by(subject='Математика').first()

    print(e)

    rows = []
    nodes = Scores()
    for n in nodes:
        a_date = datetime.strptime(n.date, "%Y-%m")
        rows.append(Examination(institution=n.id, date=a_date, grade=n.grade,
                                subject=n.subject, score=n.score,
                                students=n.students))

    session.add_all(rows)
    session.commit()

    rows = session.query(Examination).filter_by(institution='103503').all()
    for r in rows:
        print(r)

    # Close the session
    session.close()
