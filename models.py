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
from census import Censuses

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

    settlement = relationship('Settlement', back_populates='kind', uselist=True)

    def __repr__(self) -> str:
        return f"SettlementType<{self.code}, {self.label}>"


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

    settlement = relationship('Settlement', back_populates='altitude', uselist=True)

    def __repr__(self) -> str:
        return f"SettlementAltitude<{self.code}, {self.label}>"


class Settlement(Base):
    __tablename__ = "settlement"
    code = Column(String(5), primary_key=True)
    name = Column(String, nullable=False)
    municipality_abbrev = Column(Integer, ForeignKey("municipality.abbrev"))
    kind_code = Column(Integer, ForeignKey('settlement_type.code'))
    altitude_code = Column(Integer, ForeignKey('settlement_altitude.code'))

    municipality = relationship('Municipality', back_populates='settlement')
    altitude = relationship('SettlementAltitude', back_populates='settlement')
    kind = relationship('SettlementType', back_populates='settlement')

    institution = relationship('Institution', back_populates='settlement', uselist=True)
    census = relationship('Census', back_populates='settlement', uselist=True)

    def __repr__(self) -> str:
        return f"Settlement<{self.code}, {self.name}>"


class Municipality(Base):
    __tablename__ = "municipality"
    abbrev = Column(String(5), primary_key=True)
    name = Column(String, nullable=False)
    district_abbrev = Column(Integer, ForeignKey("district.abbrev"))

    district = relationship('District', back_populates='municipality')
    settlement = relationship('Settlement', back_populates='municipality', uselist=True)
    census = relationship('Census', back_populates='municipality', uselist=True)

    def __repr__(self) -> str:
        return f"Municipality<{self.abbrev}, {self.name}>"


class District(Base):
    __tablename__ = "district"
    abbrev = Column(String(3), primary_key=True)
    name = Column(String, nullable=False)

    municipality = relationship('Municipality', back_populates='district', uselist=True)

    def __repr__(self) -> str:
        return f"District<{self.abbrev}, {self.name}>"


class InstitutionFinancing(Base):
    __tablename__ = "institution_financing"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='financing', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionFinancing<{self.code}, {self.label}>"


class InstitutionDetails(Base):
    __tablename__ = "institution_details"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='details', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionDetails<{self.code}, {self.label}>"


class InstitutionState(Base):
    __tablename__ = "institution_state"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='state', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionState<{self.code}, {self.label}>"


class Institution(Base):
    __tablename__ = "institution"
    code = Column(String(7), primary_key=True)
    name = Column(String, nullable=False)
    settlement_code = Column(String, ForeignKey("settlement.code"))
    details_code = Column(Integer, ForeignKey("institution_details.code"))
    financing_code = Column(Integer, ForeignKey("institution_financing.code"))
    state_code = Column(Integer, ForeignKey("institution_state.code"))

    financing = relationship('InstitutionFinancing', back_populates='institution')
    details = relationship('InstitutionDetails', back_populates='institution')
    state = relationship('InstitutionState', back_populates='institution')
    settlement = relationship('Settlement', back_populates='institution')

    examination = relationship('Examination', back_populates='institution', uselist=True)

    def __repr__(self) -> str:
        return f"Institution<{self.code}, {self.name}>"


class ExaminationSubject(Base):
    __tablename__ = "examination_subject"
    code = Column(Integer, primary_key=True)
    subject = Column(String, primary_key=True)

    examination = relationship('Examination', back_populates='subject', uselist=True)

    def __repr__(self) -> str:
        return f"ExaminationSubject<{self.code}, {self.subject}>"


class Examination(Base):
    __tablename__ = "examination"
    index = Column(Integer, primary_key=True)
    institution_code = Column(Integer, ForeignKey("institution.code"))
    date = Column(Date)
    grade = Column(Integer)
    score = Column(Numeric)
    students = Column(Integer)
    subject_code = Column(Integer, ForeignKey("examination_subject.code"))

    institution = relationship('Institution', back_populates='examination')
    subject = relationship('ExaminationSubject', back_populates='examination')

    def __repr__(self) -> str:
        return f"Examination<{self.institution_code}, {self.date}>"


class Census(Base):
    __tablename__ = "census"
    index = Column(Integer, primary_key=True)
    settlement_code = Column(String, ForeignKey("settlement.code"))
    municipality_abbrev = Column(String, ForeignKey("municipality.abbrev"))
    date = Column(Date)
    permanent = Column(Integer)
    current = Column(Integer)

    settlement = relationship('Settlement', back_populates='census')
    municipality = relationship('Municipality', back_populates='census')

    def __repr__(self) -> str:
        return f"Census<{self.settlement_code}, {self.date}>"


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
        SettlementAltitude(code=4, label='200 - 299 вкл.'),
        SettlementAltitude(code=5, label='300 - 499 вкл.'),
        SettlementAltitude(code=6, label='500 - 699 вкл.'),
        SettlementAltitude(code=7, label='700 - 999 вкл.'),
        SettlementAltitude(code=8, label='1000 и повече'),

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
                               municipality_abbrev=n.municipality,
                               kind_code=n.kind, altitude_code=n.altitude))
    session.add_all(rows)
    session.commit()

    e = session.query(Settlement).filter_by(code='29129').first()
    print(e)

    e = session.query(Settlement).filter_by(
        name='\u0422\u0443\u0442\u0440\u0430\u043a\u0430\u043d').first()
    print(e)

    rows.clear()
    nodes = Municipalities()
    for n in nodes:
        rows.append(Municipality(abbrev=n.abbrev, name=n.name,
                    district_abbrev=n.abbrev[:3]))

    session.add_all(rows)
    session.commit()

    e = session.query(Municipality).filter_by(abbrev='BGS01').first()
    print(e)

    rows.clear()
    nodes = Districts()
    for n in nodes:
        rows.append(District(abbrev=n.abbrev, name=n.name))

    session.add_all(rows)
    session.commit()

    e = session.query(District).filter_by(abbrev='SHU').first()
    print(e)

    rows.clear()
    nodes = Finances()
    for n in nodes:
        rows.append(InstitutionFinancing(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionFinancing).filter_by(label='Духовно').first()
    print(e)

    rows.clear()
    nodes = Transforms()
    for n in nodes:
        rows.append(InstitutionState(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionState).filter_by(code=3).first()
    print(e)

    rows.clear()
    nodes = Institutions()
    for n in nodes:
        rows.append(Institution(code=n.id, name=n.name, settlement_code=n.location,
                                details_code=n.details, financing_code=n.finance,
                                state_code=n.status))
    session.add_all(rows)
    session.commit()

    rows = session.query(Institution).filter_by(code='103503').all()
    for r in rows:
        print(r)

    rows.clear()
    nodes = SchoolTypes()
    for n in nodes:
        rows.append(InstitutionDetails(code=n.code, label=n.label))

    session.add_all(rows)
    session.commit()

    e = session.query(InstitutionDetails).filter_by(label='обединено').first()
    print(e)

    rows.clear()
    nodes = Subjects()
    for n in nodes:
        rows.append(ExaminationSubject(code=n.code, subject=n.title))

    session.add_all(rows)
    session.commit()

    e = session.query(ExaminationSubject).filter_by(subject='Математика').first()

    print(e)

    rows.clear()
    nodes = Scores()
    for n in nodes:
        a_date = datetime.strptime(n.date, "%Y-%m")
        rows.append(Examination(institution_code=n.id, date=a_date, grade=n.grade,
                                subject_code=n.subject, score=n.score,
                                students=n.students))

    session.add_all(rows)
    session.commit()

    rows = session.query(Examination).filter_by(
        institution_code='103503').all()
    for r in rows:
        print(r)

    rows.clear()
    nodes = Censuses()
    for n in nodes:
        a_date = datetime.strptime(n.date, "%d.%m.%Y")
        rows.append(Census(settlement_code=n.code, municipality_abbrev=n.municipality,
                           date=a_date, permanent=n.permanent,
                           current=n.current))

    session.add_all(rows)
    session.commit()

    rows = session.query(Census).filter_by(settlement_code='12259').all()
    for r in rows:
        print(r)

    # Close the session
    session.close()
