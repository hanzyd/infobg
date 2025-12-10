#!/usr/bin/env python3

from datetime import date

from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine, MetaData

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm import DeclarativeBase


# https://github.com/sqlalchemy/alembic/discussions/1559
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

# - Код на типа на териториалната единица:
#   1  "гр. "  -  град
#   3  "с.  "  -  село
#   7  "ман."  -  манастир
class SettlementType(Base):
    __tablename__ = "settlement_type"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща типа на населеното място (село, град, манастир).
        """
    }

    c = """
            Уникален идентификатор за типа на населеното мястно
            (град, село или манастир).

            Използва се като външен ключ (foreign key) в свързаната
            таблица населено място (settlement).
        """
    id = Column(Integer, primary_key=True, comment=c)

    c = """
            тип на населеното място. "гр." за град, "с." за село,
            "ман." за манастир
        """
    label = Column(String, comment=c)

    settlement = relationship('Settlement', back_populates='settlement_type', uselist=True)

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
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща надморската височина на населеното място, в метри.
        """
    }

    c = """
            Уникален идентификатор за надморската височина на
            населеното мястно.

            Използва се като външен ключ (foreign key) в свързаната
            таблица населено място (settlement).
        """
    id = Column(Integer, primary_key=True, comment=c)

    c = """
            1 = до 49 вкл.
            2 = 50 - 99 вкл.
            3 = 100 - 199 вкл.
            4 = 200 - 299 вкл.
            5 = 300 - 499 вкл.
            6 = 500 - 699 вкл.
            7 = 700 - 999 вкл.
            8 = 1000 и повече
        """
    label = Column(String, nullable=False, comment=c)

    settlement = relationship('Settlement', back_populates='altitude', uselist=True)

    def __repr__(self) -> str:
        return f"SettlementAltitude<{self.label}>"


class Settlement(Base):
    __tablename__ = "settlement"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща описанието на населените мяста.

            Населено място е исторически и функционално обособена територия,
            определена с наличието на постоянно живеещо население, строителни
            граници или землищни и строителни граници и необходимата социална и
            инженерна инфраструктура.
            Населените места се делят на градове и села и подлежат на регистрация
            в единния класификатор на административно-териториалните и
            териториални единици.
        """
    }

    c = """
            Уникален идентификатор на населеното мястно (settlement).
            Използва се като външен ключ (foreign key) в свързаните
            таблици:
            - като учебно заведение (училище) (institution)
            - преброяване (census).
        """
    id = Column(Integer, primary_key=True, autoincrement=True, comment=c)

    c = 'Петбуквен идентификационен код на населено място'
    code = Column(String(5), unique=True, comment=c)

    c = 'Име на населеното място'
    name = Column(String, nullable=False, comment=c)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = """
            Улазател в таблицата с типовете на населените места (град,
            село или манастир)
        """
    type_id = Column(Integer, ForeignKey('settlement_type.id', comment=c))

    c = """
            Улазател в таблицата с надмосрката височина на населени места,
            в метри
        """
    altitude_id = Column(Integer, ForeignKey('settlement_altitude.id', comment=c))

    municipality = relationship('Municipality', back_populates='settlement')
    altitude = relationship('SettlementAltitude', back_populates='settlement')
    settlement_type = relationship('SettlementType', back_populates='settlement')

    institution = relationship('Institution', back_populates='settlement', uselist=True)
    census = relationship('Census', back_populates='settlement', uselist=True)

    def __repr__(self) -> str:
        return f"Settlement<{self.name}>"


class Municipality(Base):
    __tablename__ = "municipality"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща описанието на община (municipality).

            Общината е административно-териториалните единици, в които основно
            се осъществява местното самоуправление в България.
            Общината се състои от едно или повече съседни населени места.
            Територия на общината е територията на включените в нея населени
            места.
        """
    }

    c = """
            Уникален идентификатор за община (municipality).

            Използва се като външен ключ (foreign key) в свързаните
            таблици:

            - Област (district)
            - Населено място (settlement)
            - Преброяване (census)
            - Майчин език (mother_tongue)
            - Етничека принадлежност (ethnicity)
            - Религия (religion)
            - Образувание (education)
            - Грамотност (literacy)
        """
    id = Column(Integer, primary_key=True, autoincrement=True, comment=c)

    c = 'Петбуквен идентификационен код на общината (абревиатура)'
    abbrev = Column(String(5), unique=True, comment=c)

    name = Column(String, nullable=False, comment='Име на общината')

    c = 'Улазател в таблицата на областите'
    district_id = Column(Integer, ForeignKey("district.id"), comment=c)

    district = relationship('District', back_populates='municipality')
    settlement = relationship('Settlement', back_populates='municipality', uselist=True)
    census = relationship('Census', back_populates='municipality', uselist=True)
    mother_tongue = relationship('MotherTongue', back_populates='municipality', uselist=True)
    ethnicity = relationship('Ethnicity', back_populates='municipality', uselist=True)
    religion = relationship('Religion', back_populates='municipality', uselist=True)
    education = relationship('Education', back_populates='municipality', uselist=True)
    literacy = relationship('Literacy', back_populates='municipality', uselist=True)

    def __repr__(self) -> str:
        return f"Municipality<{self.abbrev}, {self.name}>"


class District(Base):
    __tablename__ = "district"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща описанието на административен окръг.

            Областта се състои от една или повече съседни общини.
            Наименование на областта е наименованието на населеното място - неин
            административен център.
        """
    }

    c = """
            Уникален идентификатор за област (district).

            Използва се като външен ключ (foreign key) в свързаната
            таблицa:
            - община (municipality).
        """
    id = Column(Integer, primary_key=True, autoincrement=True, comment=c)

    c = 'Трибуквен идентификационен код на областа (абревиатура)'
    abbrev = Column(String(3), unique=True, comment=c)

    name = Column(String(25), nullable=False, unique=True, comment='Име на областа')

    municipality = relationship('Municipality', back_populates='district', uselist=True)

    def __repr__(self) -> str:
        return f"District<{self.abbrev}, {self.name}>"


class InstitutionFinancing(Base):
    __tablename__ = "institution_financing"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък по типа на форма на собственост
            на учебната институция (училище).
        """
    }

    c = """
            Уникален идентификатор за на типа финасиране
            на учебната институция (училище).

            Използва се като външен ключ (foreign key) в свързаната
            таблица населено място (settlement).
        """
    id = Column(Integer, primary_key=True, comment=c)

    c = """
            Наименование на типа финансиране (общинско, държавно,
            частно и др.)
        """
    label = Column(String, nullable=False, comment=c)

    institution = relationship('Institution', back_populates='financing', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionFinancing<{self.label}>"


class InstitutionDetails(Base):
    __tablename__ = "institution_details"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък учебнатите институции (училиша)
            по техния вид (основно, средно, гимазия и др.)
        """
    }

    c = """
            Уникален удентификационен код на вида на учебната
            институция (училище).

            Използва се като външен ключ (foreign key) в свързаната
            таблица учебно заведение (училище) (institution).
        """
    id = Column(Integer, primary_key=True, comment=c)

    c = """
           Наименование на вида на учебната институция (основно,
           спортно, професионална гимназия и др.
        """
    label = Column(String, nullable=False, comment=c)

    institution = relationship('Institution', back_populates='details', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionDetails<{self.label}>"


class InstitutionStatus(Base):
    __tablename__ = "institution_status"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък текущото състояние на учебнатите
            институции (действащи, закрито и др.)
        """
    }

    c = """
            Уникален идентификационен код а текущото състояние на
            учебната институция (училище).

            Използва се като външен ключ (foreign key) в свързаната
            таблица учебно заведение (училище) (institution).
        """
    id = Column(Integer, primary_key=True, comment=c)

    c = """
           Наименование на текущото състояние на учебнатите
           институции (действащо, закрито и др.
        """
    label = Column(String, nullable=False, comment=c)

    institution = relationship('Institution', back_populates='status', uselist=True)

    def __repr__(self) -> str:
        return f"InstitutionStatus<{self.label}>"


class Institution(Base):
    __tablename__ = "institution"
    __table_args__ = {
        'comment':
        """
            Таблицата съдържа информация за институциите в системата на
            предучилищното и училищното образование в Република България:

            - Държавни детски градини, държавни и общински училища и държавните и
              общински центрове за специална образователна подкрепа
            - Специализирани обслужващи звена
            - Духовни училища
            - Частни детски градини и училища
        """
    }

    c = """
            Уникален идентификационен код на учебната институция
            (училище).

            Използва се като външен ключ (foreign key) в свързаната
            таблица с резултати от изпити (examination).
        """
    id = Column(Integer, primary_key=True, autoincrement=True, comment=c)

    c = """
            Уникален шестцифрен код на учебното институция.

            Той е част от общ регистър за образователни институции и
            служи за електронна обработка на данни, финансиране,
            статистически справки и обмен на информация (напр. в
            електронните дневници и информационни системи на МОН
        """
    code = Column(String(7), unique=True, comment=c)

    c = """
          Пълно наименование на образователната институция (училище)
        """
    name = Column(String, nullable=False, comment=c)

    c = 'Указател към таблицата с населените места'
    settlement_id = Column(Integer, ForeignKey("settlement.id", comment=c))

    c = 'Указател към таблицата с вида на учебнатите институции.'
    details_id = Column(Integer, ForeignKey("institution_details.id", comment=c))

    c = """
            Указател към таблицата с типа на форма на собственост на
            учебната институция
        """
    financing_id = Column(Integer, ForeignKey("institution_financing.id", comment=c))

    c = 'Указател към таблицата с населените места'
    status_id = Column(Integer, ForeignKey("institution_status.id", comment=c))

    financing = relationship('InstitutionFinancing', back_populates='institution')
    details = relationship('InstitutionDetails', back_populates='institution')
    status = relationship('InstitutionStatus', back_populates='institution')
    settlement = relationship('Settlement', back_populates='institution')

    examination = relationship('Examination', back_populates='institution', uselist=True)

    def __repr__(self) -> str:
        return f"Institution<{self.code}, {self.name}>"


class ExaminationSubject(Base):
    __tablename__ = "examination_subject"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък с темите на държавените зрелостенни
            изпити.

            Някои от темите са:
            - Български език и литература
            - математика;
            - чужд език (по избор: английски, руски, немски, френски, испански, италиански);
            - история и цивилизация;
            - география и икономика;
            - философски цикъл;
            - химия и опазване на околната среда;
            - биология и здравно образование;
            - физика и астрономия.
        """
    }

    c = """
            Уникален идентификационен код на темата на изпита.

            Използва се като външен ключ (foreign key) в свързаната
            таблица с резултат (examination)
        """
    id = Column(Integer, primary_key=True, comment=c)

    subject = Column(String, comment='Наименование на темата на изпита')

    examination = relationship('Examination', back_populates='subject', uselist=True)

    def __repr__(self) -> str:
        return f"ExaminationSubject<{self.subject}>"


class Examination(Base):
    __tablename__ = "examination"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък с резултатите от матите или държавен
            зрелостен изпит в учебните заведения.

            В края на учебната година се държи матура по два предмета –
            задължително по Български език и литература, а вторият предмет
            е по избор на зрелостника от следните дисциплини:
            - математика;
            - чужд език (по избор: английски, руски, немски, френски, испански,
              италиански);
            - история и цивилизация;
            - география и икономика;
            - философски цикъл;
            - химия и опазване на околната среда;
            - биология и здравно образование;
            - физика и астрономия.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Указател към таблицата с учебните заведения'
    institution_id = Column(Integer, ForeignKey("institution.id", comment=c))

    c = 'Указател към таблицата с датите на проведените изпити'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    c = """
            Учебен клас.

            Клас се нарича формална група ученици в начално, основно или средно
            училище разделени по възрастов признак.

            Класовете от 1. до 4. съставляват начален курс на обучение,
            а училището (ако е самостоятелно) се нарича начално училище.

            Класовете от 5. до 7. клас съставляват среден курс на обучение, а
            училището (ако е самостоятелно) – прогимназия или основно училище.

            Класовете от 8. до 12. клас съставляват горен курс на обучение, а
            училището (ако е самостоятелно) – гимназия или средно училище
        """
    grade = Column(Integer, comment=c)

    c = """
           Осреднена оценка от изпит по дадена тема в зависимост от броя ученици
           участвали на изпита за съответната образоватерлна институция
        """
    score = Column(Numeric, comment=c)

    students = Column(Integer, comment='Брой ученици участвали на изпита')

    c = 'Указател към таблицата с темите на изпитите.'
    subject_id = Column(Integer, ForeignKey("examination_subject.id", comment=c))

    institution = relationship('Institution', back_populates='examination')
    subject = relationship('ExaminationSubject', back_populates='examination')
    moment = relationship('Moment', back_populates='examination')

    def __repr__(self) -> str:
        return f"Examination<{self.institution_id:5}, {self.date_id:3} {self.score:5.4}>"


class Moment(Base):
    __tablename__ = "moment"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща списък на датите на които са проведени изпити или
            препрояване на населениетп.
        """
    }

    c = """
            Уникален код на дата.

            Използва се като външен ключ (foreign key) в свързаните таблици:
            - резултат от изпит (examination)
            - преброяване на населението (census)
            - майчин език (мother_тongue)
            - етническа принадлежност (ethnicity)
            - изповядвана религия (religion)
            - образование (education)
            - грамотност на населението (literacy)
        """
    id = Column(Integer, primary_key=True, autoincrement=True, comment=c)

    c = 'Дата на провеждане на преброяването или изпита'
    date = Column(Date, unique=True, comment=c)

    census = relationship('Census', back_populates='moment', uselist=True)
    examination = relationship('Examination', back_populates='moment', uselist=True)
    mother_tongue = relationship('MotherTongue', back_populates='moment', uselist=True)
    ethnicity = relationship('Ethnicity', back_populates='moment', uselist=True)
    religion = relationship('Religion', back_populates='moment', uselist=True)
    education = relationship('Education', back_populates='moment', uselist=True)
    literacy = relationship('Literacy', back_populates='moment', uselist=True)

    def __repr__(self) -> str:
        return f"Moment<{self.date}>"

    @staticmethod
    def insert_date(moment: date, session: Session) -> int:

        d_index = session.query(Moment.id).filter_by(date=moment).first()
        if not d_index:
            m = Moment(date=moment)
            session.add(m)
            session.commit()
            d_index = session.query(Moment.id).filter_by(date=moment).first()

        if d_index:
            return d_index[0]
        else:
            return -1


class Census(Base):
    __tablename__ = "census"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща информация сързана с преброяванията на
            населението в отделните общини в България за съответната година.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Указател към таблицата с населените места'
    settlement_id = Column(Integer, ForeignKey("settlement.id", comment=c))

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    permanent = Column(Integer, comment='Брой на жителите по постоянен адрес')
    current = Column(Integer, comment='Брой на жителите по настоящ адрес')

    settlement = relationship('Settlement', back_populates='census')
    municipality = relationship('Municipality', back_populates='census')
    moment = relationship('Moment', back_populates='census')

    def __repr__(self) -> str:
        return f"Census<{self.settlement_id}, {self.date_id}>"


class MotherTongue(Base):
    __tablename__ = "mother_tongue"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща разпределението, в процентно съотношение
            по майчен език, в съответната община и дата. Данните в колоните
            са в проценти.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    bulgarians = Column(Integer, comment='Български, в проценти')
    turks = Column(Integer, comment='Турски, в проценти')
    roma = Column(Integer, comment='Ромски, в проценти')
    other = Column(Integer, comment='Друг, в проценти')
    cant_decide = Column(Integer, comment='Не мога да определя, в проценти')
    dont_answer = Column(Integer, comment='Не желая да отговоря, в проценти')
    not_shown = Column(Integer, comment='Непоказан, в проценти')

    municipality = relationship('Municipality', back_populates='mother_tongue')
    moment = relationship('Moment', back_populates='mother_tongue')

    def __init__(self, m_id: int, d_id: int, total: int, bulgarians: int,
                 turks: int, roma: int, other: int, cant_decide: int,
                 dont_answer: int, not_shown: int):

        x = bulgarians + turks + roma + other + cant_decide + dont_answer + not_shown
        if x != total:
            print(f'език: общия брой се различва {total} != {x}')

        self.municipality_id = m_id
        self.date_id = d_id
        self.bulgarians = round(float(bulgarians) * 100.0 / float(x))
        self.turks = round(float(turks) * 100.0 / float(x))
        self.roma = round(float(roma) * 100.0 / float(x))
        self.other = round(float(other) * 100.0 / float(x))
        self.cant_decide = round(float(cant_decide) * 100.0 / float(x))
        self.dont_answer = round(float(dont_answer) * 100.0 / float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

        # x = self.bulgarians + self.turks + self.roma + self.other + \
        #     self.cant_decide + self.dont_answer + self.not_shown
        # if x != 100:
        #     print(f'език: общия процент {x} != 100')

    def __repr__(self):
        return f'Език<{self.municipality_id:3} български: {self.bulgarians:2}% турски: {self.turks:2}% ромски: {self.roma:2}%>'


class Ethnicity(Base):
    __tablename__ = "ethnicity"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща разпределението по етническа принадлежност,
            в съответната община и дата. Данните в колоните са в проценти.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    bulgarians = Column(Integer, comment='Български, в проценти')
    turks = Column(Integer, comment='Турски, в проценти')
    roma = Column(Integer, comment='Ромски, в проценти')
    other = Column(Integer, comment='Друг, в проценти')
    cant_decide = Column(Integer, comment='Не мога да определя, в проценти')
    dont_answer = Column(Integer, comment='Не желая да отговоря, в проценти')
    not_shown = Column(Integer, comment='Непоказан, в проценти')

    municipality = relationship('Municipality', back_populates='ethnicity')
    moment = relationship('Moment', back_populates='ethnicity')

    def __init__(self, m_id: int, d_id: int, total: int, bulgarians: int,
                 turks: int, roma: int, other: int, cant_decide: int,
                 dont_answer: int, not_shown: int):

        x = bulgarians + turks + roma + other + cant_decide + dont_answer + not_shown
        if x != total:
            print(f'етност: общия брой се различва {total} != {x}')

        self.municipality_id = m_id
        self.date_id = d_id
        self.bulgarians = round(float(bulgarians) * 100.0 / float(x))
        self.turks = round(float(turks) * 100.0 / float(x))
        self.roma = round(float(roma) * 100.0 / float(x))
        self.other = round(float(other) * 100.0 / float(x))
        self.cant_decide = round(float(cant_decide) * 100.0 / float(x))
        self.dont_answer = round(float(dont_answer) * 100.0 / float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

        # x = self.bulgarians + self.turks + self.roma + self.other + \
        #     self.cant_decide + self.dont_answer + self.not_shown
        # if x != 100:
        #     print(f'етност: общия процент {x} != 100')

    def __repr__(self):
        return f'Етнос<{self.municipality_id:3} българи: {self.bulgarians:2}% турци: {self.turks:2}% роми: {self.roma:2}%>'


class Religion(Base):
    __tablename__ = "religion"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща разпределението на населението по вероизповедание
            в съответната община и дата. Данните в колоните са в проценти.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    orthodox = Column(Integer, comment='Християнско, в проценти')
    muslims = Column(Integer, comment='Мюсюлманско, в проценти')
    judean = Column(Integer, comment='Юдейско, в проценти')
    other = Column(Integer, comment='Друго, в проценти')
    none = Column(Integer, comment='Нямам, в проценти')
    cant_decide = Column(Integer, comment='Не мога да определя, в проценти')
    dont_answer = Column(Integer, comment='Не желая да отговоря, в проценти')
    not_shown = Column(Integer, comment='Непоказано, в проценти')

    municipality = relationship('Municipality', back_populates='religion')
    moment = relationship('Moment', back_populates='religion')

    def __init__(self, m_id: int, d_id: int, total: int, orthodox: int,
                 muslims: int, judean: int, other: int, none: int,
                 cant_decide: int, dont_answer: int, not_shown: int):

        x = orthodox + muslims + judean + other + \
            none + cant_decide + dont_answer + not_shown
        if x != total:
            print(f'религия: общия брой се различва {total} != {x}')

        self.municipality_id = m_id
        self.date_id = d_id
        self.orthodox = round(float(orthodox) * 100.0 / float(x))
        self.muslims = round(float(muslims) * 100.0 / float(x))
        self.judean = round(float(judean) * 100.0 / float(x))
        self.other = round(float(other) * 100.0 / float(x))
        self.none = round(float(none) * 100.0 / float(x))
        self.cant_decide = round(float(cant_decide) * 100.0 / float(x))
        self.dont_answer = round(float(dont_answer) * 100.0 / float(x))
        self.not_shown = round(float(not_shown) * 100.0 / float(x))

        # x = self.orthodox + self.muslims + self.judean + self.other + \
        #     self.none + self.cant_decide + self.dont_answer + self.not_shown
        # if x != 100:
        #     print(f'религия: общия процент {x} != 100')

    def __repr__(self):
        return f'Религия<{self.municipality_id:3} християни: {self.orthodox:2}% мюслмани: {self.muslims:2}% юдеи: {self.judean:2}%>'


class Education(Base):
    __tablename__ = "education"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща разпределението на образователна структура на
            населението на 7 и повече години по степен на образование,
            община и дата. Данните в колоните са в проценти.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    university = Column(Integer, comment='Висше образование, в проценти')
    secondary = Column(Integer, comment='Средно образование, в проценти')
    primary = Column(Integer, comment='Основно образование, в проценти')
    elementary = Column(
        Integer, comment='Начално и по-ниско образование, в проценти')
    no_school = Column(
        Integer, comment='Дете до 7 години включително, което още не посещава училище, в проценти')

    municipality = relationship('Municipality', back_populates='education')
    moment = relationship('Moment', back_populates='education')

    def __init__(self, m_id: int, d_id: int, total: int, university: int,
                 secondary: int, primary: int, elementary: int, none: int):

        x = university + secondary + primary + elementary + none
        if x != total:
            print(f'образование: общия брой се различва {total} != {x}')

        self.municipality_id = m_id
        self.date_id = d_id
        self.university = round(float(university) * 100.0 / float(x))
        self.secondary = round(float(secondary) * 100.0 / float(x))
        self.primary = round(float(primary) * 100.0 / float(x))
        self.elementary = round(float(elementary) * 100.0 / float(x))
        self.no_school = round(float(none) * 100.0 / float(x))

        # x = self.university + self.secondary + \
        #     self.primary + self.elementary + self.no_school
        # if x != 100:
        #     print(f'образование: общия процент {x} != 100')

    def __repr__(self):
        return f'Образование<{self.municipality_id:3} Висше: {self.university:2}% Средно: {self.secondary:2}% Основно: {self.primary:2}%>'


class Literacy(Base):
    __tablename__ = "literacy"
    __table_args__ = {
        'comment':
        """
            Таблица, съдържаща разпределението на грамотните и неграмотните по
            община и дата. Данните в колоните са в проценти.
        """
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    c = 'Улазател към таблицата на общините'
    municipality_id = Column(Integer, ForeignKey("municipality.id", comment=c))

    c = 'Указател към таблицата с датите на проведените преборявания'
    date_id = Column(Integer, ForeignKey("moment.id", comment=c))

    literate = Column(Integer, comment='Грамотни, в проценти')
    illiterate = Column(Integer, comment='Неграмотни, в проценти')

    municipality = relationship('Municipality', back_populates='literacy')
    moment = relationship('Moment', back_populates='literacy')

    def __init__(self, m_id: int, d_id: int, total: int, literate: int,
                 iletarate: int):

        x = literate + iletarate
        if x != total:
            print(f'грамотност: общия брой се различва {total} != {x}')

        self.municipality_id = m_id
        self.date_id = d_id
        self.literate = round(float(literate) * 100.0 / float(x))
        self.illiterate = round(float(iletarate) * 100.0 / float(x))

        # x = self.literate + self.illiterate
        # if x != 100:
        #     print(f'грамотност: общия процент {x} != 100')

    def __repr__(self):
        return f'Грамотност<{self.municipality_id:3} грамотни: {self.literate:2}% неграмотни: {self.illiterate:2}%>'


if __name__ == "__main__":

    engine = create_engine("postgresql://localhost/infobg")
    if not database_exists(engine.url):
        create_database(engine.url)
    else:
        drop_database(engine.url)
        create_database(engine.url)

    # Create all tables in the engine
    Base.metadata.create_all(engine)
    pass
