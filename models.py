#!/usr/bin/env python3

from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm import declarative_base

# from locations import Locations
# from finance import Finances
# from details import SchoolTypes
# from subjects import Subjects
# from scores import Scores
# from transform import Transforms
# from institutions import Institutions
# from census import Censuses

Base = declarative_base()

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
        return f"SettlementType<{self.label}>"


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
        return f"SettlementAltitude<{self.label}>"


class Settlement(Base):
    __tablename__ = "settlement"
    index = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(5), unique=True)
    name = Column(String, nullable=False)
    municipality_index = Column(Integer, ForeignKey("municipality.index"))
    kind_code = Column(Integer, ForeignKey('settlement_type.code'))
    altitude_code = Column(Integer, ForeignKey('settlement_altitude.code'))

    municipality = relationship('Municipality', back_populates='settlement')
    altitude = relationship('SettlementAltitude', back_populates='settlement')
    kind = relationship('SettlementType', back_populates='settlement')

    institution = relationship('Institution', back_populates='settlement', uselist=True)
    census = relationship('Census', back_populates='settlement', uselist=True)

    def __repr__(self) -> str:
        return f"Settlement<{self.name}>"


class Municipality(Base):
    __tablename__ = "municipality"
    index = Column(Integer, primary_key=True, autoincrement=True)
    abbrev = Column(String(5), unique=True)
    name = Column(String, nullable=False)
    district_index = Column(Integer, ForeignKey("district.index"))

    district = relationship('District', back_populates='municipality')
    settlement = relationship('Settlement', back_populates='municipality', uselist=True)
    census = relationship('Census', back_populates='municipality', uselist=True)
    mother_tongue = relationship('MotherTongue', back_populates='municipality', uselist=True)
    ethnicity = relationship('Ethnicity', back_populates='municipality', uselist=True)
    religion = relationship('Religion', back_populates='municipality', uselist=True)

    def __repr__(self) -> str:
        return f"Municipality<{self.abbrev}, {self.name}>"


class District(Base):
    __tablename__ = "district"
    index = Column(Integer, primary_key=True, autoincrement=True)
    abbrev = Column(String(3), unique=True)
    name = Column(String(25), nullable=False, unique=True)

    municipality = relationship('Municipality', back_populates='district', uselist=True)

    def __repr__(self) -> str:
        return f"District<{self.abbrev}, {self.name}>"


class InstitutionFinancing(Base):
    __tablename__ = "institution_financing"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='financing', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionFinancing<{self.label}>"


class InstitutionDetails(Base):
    __tablename__ = "institution_details"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='details', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionDetails<{self.label}>"


class InstitutionStatus(Base):
    __tablename__ = "institution_status"
    code = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    institution = relationship('Institution', back_populates='status', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionStatus<{self.label}>"


class Institution(Base):
    __tablename__ = "institution"
    index = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(7), unique=True)
    name = Column(String, nullable=False)
    settlement_index = Column(Integer, ForeignKey("settlement.index"))
    details_code = Column(Integer, ForeignKey("institution_details.code"))
    financing_code = Column(Integer, ForeignKey("institution_financing.code"))
    status_code = Column(Integer, ForeignKey("institution_status.code"))

    financing = relationship('InstitutionFinancing', back_populates='institution')
    details = relationship('InstitutionDetails', back_populates='institution')
    status = relationship('InstitutionStatus', back_populates='institution')
    settlement = relationship('Settlement', back_populates='institution')

    examination = relationship('Examination', back_populates='institution', uselist=True)

    def __repr__(self) -> str:
        return f"Institution<{self.code}, {self.name}>"


class ExaminationSubject(Base):
    __tablename__ = "examination_subject"
    code = Column(Integer, primary_key=True)
    subject = Column(String)

    examination = relationship('Examination', back_populates='subject', uselist=True)

    def __repr__(self) -> str:
        return f"ExaminationSubject<{self.subject}>"


class Examination(Base):
    __tablename__ = "examination"
    index = Column(Integer, primary_key=True, autoincrement=True)
    institution_index = Column(Integer, ForeignKey("institution.index"))
    date_index = Column(Integer, ForeignKey("moment.index"))
    grade = Column(Integer)
    score = Column(Numeric)
    students = Column(Integer)
    subject_code = Column(Integer, ForeignKey("examination_subject.code"))

    institution = relationship('Institution', back_populates='examination')
    subject = relationship('ExaminationSubject', back_populates='examination')
    moment = relationship('Moment', back_populates='examination')

    def __repr__(self) -> str:
        return f"Examination<{self.institution_index:5}, {self.date_index:3} {self.score:5.4}>"

class Moment(Base):
    __tablename__ = "moment"
    index = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True)

    census = relationship('Census', back_populates='moment', uselist=True)
    examination = relationship('Examination', back_populates='moment', uselist=True)
    mother_tongue = relationship('MotherTongue', back_populates='moment', uselist=True)
    ethnicity = relationship('Ethnicity', back_populates='moment', uselist=True)
    religion = relationship('Religion', back_populates='moment', uselist=True)

    def __repr__(self) -> str:
        return f"Moment<{self.date}>"


class Census(Base):
    __tablename__ = "census"
    index = Column(Integer, primary_key=True, autoincrement=True)
    settlement_index = Column(Integer, ForeignKey("settlement.index"))
    municipality_index = Column(Integer, ForeignKey("municipality.index"))
    date_index = Column(Integer, ForeignKey("moment.index"))
    permanent = Column(Integer)
    current = Column(Integer)

    settlement = relationship('Settlement', back_populates='census')
    municipality = relationship('Municipality', back_populates='census')
    moment = relationship('Moment', back_populates='census')

    def __repr__(self) -> str:
        return f"Census<{self.settlement_index}, {self.date_index}>"


class MotherTongue(Base):
    __tablename__ = "mother_tongue"
    index = Column(Integer, primary_key=True, autoincrement=True)
    municipality_index = Column(Integer, ForeignKey("municipality.index"))
    date_index = Column(Integer, ForeignKey("moment.index"))
    bulgarians = Column(Integer)
    turks = Column(Integer)
    roma = Column(Integer)
    other = Column(Integer)
    cant_decide = Column(Integer)
    dont_answer = Column(Integer)
    not_shown = Column(Integer)

    municipality = relationship('Municipality', back_populates='mother_tongue')
    moment = relationship('Moment', back_populates='mother_tongue')

    def __init__(self, m_index: int, d_index: int, total: int, bulgarians:int,
                 turks: int, roma: int, other: int, cant_decide: int,
                 dont_answer: int, not_shown: int):

        x = bulgarians + turks + roma + other + cant_decide + dont_answer + not_shown
        if x != total:
            print('език: общия брой се различва {total} != {x}')

        self.municipality_index = m_index
        self.date_index = d_index
        self.bulgarians = round(float(bulgarians) * 100.0 / float(x))
        self.turks = round(float(turks) * 100.0 / float(x))
        self.roma = round(float(roma)  * 100.0/ float(x))
        self.other = round(float(other) * 100.0  / float(x))
        self.cant_decide = round(float(cant_decide)  * 100.0/ float(x))
        self.dont_answer = round(float(dont_answer)  * 100.0/ float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

    def __repr__(self):
        return f'Език<{self.municipality_index:3} български: {self.bulgarians:2}% турски: {self.turks:2}% ромски: {self.roma:2}%>'


class Ethnicity(Base):
    __tablename__ = "ethnicity"
    index = Column(Integer, primary_key=True, autoincrement=True)
    municipality_index = Column(Integer, ForeignKey("municipality.index"))
    date_index = Column(Integer, ForeignKey("moment.index"))
    bulgarians = Column(Integer)
    turks = Column(Integer)
    roma = Column(Integer)
    other = Column(Integer)
    cant_decide = Column(Integer)
    dont_answer = Column(Integer)
    not_shown = Column(Integer)

    municipality = relationship('Municipality', back_populates='ethnicity')
    moment = relationship('Moment', back_populates='ethnicity')

    def __init__(self, m_index: int, d_index: int, total: int, bulgarians:int,
                 turks: int, roma: int, other: int, cant_decide: int,
                 dont_answer: int, not_shown: int):

        x = bulgarians + turks + roma + other + cant_decide + dont_answer + not_shown
        if x != total:
            print('етност: общия брой се различва {total} != {x}')

        self.municipality_index = m_index
        self.date_index = d_index
        self.bulgarians = round(float(bulgarians) * 100.0 / float(x))
        self.turks = round(float(turks) * 100.0 / float(x))
        self.roma = round(float(roma)  * 100.0/ float(x))
        self.other = round(float(other) * 100.0  / float(x))
        self.cant_decide = round(float(cant_decide)  * 100.0/ float(x))
        self.dont_answer = round(float(dont_answer)  * 100.0/ float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

    def __repr__(self):
        return f'Етнос<{self.municipality_index:3} българи: {self.bulgarians:2}% турци: {self.turks:2}% роми: {self.roma:2}%>'


class Religion(Base):
    __tablename__ = "religion"
    index = Column(Integer, primary_key=True, autoincrement=True)
    municipality_index = Column(Integer, ForeignKey("municipality.index"))
    date_index = Column(Integer, ForeignKey("moment.index"))
    orthodox = Column(Integer)
    muslims = Column(Integer)
    judean = Column(Integer)
    other = Column(Integer)
    none = Column(Integer)
    cant_decide = Column(Integer)
    dont_answer = Column(Integer)
    not_shown = Column(Integer)

    municipality = relationship('Municipality', back_populates='religion')
    moment = relationship('Moment', back_populates='religion')

    def __init__(self, m_index: int, d_index: int, total: int, orthodox:int,
                 muslims: int, judean: int, other: int, none: int,
                 cant_decide: int, dont_answer: int, not_shown: int):

        x = orthodox + muslims + judean + other + none + cant_decide + dont_answer + not_shown
        if x != total:
            print('религия: общия брой се различва {total} != {x}')

        self.municipality_index = m_index
        self.date_index = d_index
        self.orthodox = round(float(orthodox) * 100.0 / float(x))
        self.muslims = round(float(muslims) * 100.0 / float(x))
        self.judean = round(float(judean)  * 100.0/ float(x))
        self.other = round(float(other) * 100.0  / float(x))
        self.none = round(float(none)  * 100.0/ float(x))
        self.cant_decide = round(float(cant_decide)  * 100.0/ float(x))
        self.dont_answer = round(float(dont_answer)  * 100.0/ float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

    def __repr__(self):
        return f'Религия<{self.municipality_index:3} християни: {self.orthodox:2}% мюслмани: {self.muslims:2}% юдеи: {self.judean:2}%>'

if __name__ == "__main__":

    engine = create_engine("postgresql://localhost/infobg")
    if not database_exists(engine.url):
        create_database(engine.url)

    # Create all tables in the engine
    Base.metadata.create_all(engine)

    classes = [
        Census, MotherTongue, Religion, Ethnicity,
        Examination, ExaminationSubject,
        Institution, InstitutionStatus, InstitutionDetails, InstitutionFinancing,
        Settlement, SettlementAltitude, SettlementType, Moment,
        Municipality, District
    ]

    with Session(engine) as session:
        for cls in classes:
            session.query(cls).delete()
            session.commit()

    pass
