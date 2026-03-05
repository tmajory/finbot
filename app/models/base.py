from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column, declarative_base, Session, Mapped

Base = declarative_base()

#Base class of the database with general methods

class BaseModel(Base):
    __abstract__ = True

    id : Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)

    def __repr__(self):
        """Represantation instance method"""
        attrs = []
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                attrs.append(f"{key}={value}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"
    
    def to_dict(self):
        """Instance convert method to dictionary to access the atributes easily"""
        return {
            column.name: getattr(self,column.name)
            for column in self.__table__.columns
        }

    def set_attributes(self, **kwargs):
        """Setter method"""
        for key, value in kwargs.items():
            self.__setattr__(key,value)
        return self

    def save(self, session: Session, **kwargs):
        """Method that saves a instance using sqlalchemy strategy"""
        instance = self.set_attributes(**kwargs)
        try:
            session.merge(instance)
            session.commit()
            return True, None #Return if the save success
        except Exception as e:
            session.rollback()
            return False, e #Return if fails
        
    def delete(self, session: Session):
        """Hard delete!"""
        try:
            session.delete(self)
            session.commit()
            return True, None #Return if success
        except Exception as e:
            session.rollback()
            return  False, e #Return if fails
