from domain.Image import Image
from domain.base import Base
from domain.Episode import Episode
from domain.VideoFile import VideoFile
from sqlalchemy import Column, Integer, TEXT, DATE, TIMESTAMP, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime


class Bangumi(Base):
    __tablename__ = 'bangumi'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4)
    bgm_id = Column(Integer, nullable=False, unique=True)
    name = Column(TEXT, nullable=False)
    name_cn = Column(TEXT, nullable=False)
    type = Column(Integer, nullable=False)
    eps = Column(Integer, nullable=False)
    summary = Column(TEXT, nullable=False)
    # The bangumi cover url from the bgm.tv
    image = Column(TEXT, nullable=False)
    air_date = Column(DATE, nullable=False)
    air_weekday = Column(Integer, nullable=False)
    # @deprecated
    rss = Column(TEXT, nullable=True)
    # dmhy search criteria
    dmhy = Column(TEXT, nullable=True)
    eps_no_offset = Column(Integer, nullable=True)
    # acg.rip search criteria
    acg_rip = Column(TEXT, nullable=True)
    # libyk.so search criteria, this field should be an JSON string contains two fields: {t: string, q: string}
    libyk_so = Column(TEXT, nullable=True)
    # bangumi.moe tag id array, this field should be an serialized JSON array contains strings
    bangumi_moe = Column(TEXT, nullable=True)
    # @deprecated
    eps_regex = Column(TEXT, nullable=True)
    status = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now, nullable=False)
    update_time = Column(TIMESTAMP, default=datetime.now, nullable=False)

    # dominant color extracted from current bangumi cover image
    # @deprecated
    cover_color = Column(String, nullable=True)

    cover_image_id = Column(postgresql.UUID(as_uuid=True), nullable=True)

    # this mark is used by DeleteScanner to start a task for deleting certain bangumi and all data associated.
    # it is a date time when bangumi is schedule to delete
    delete_mark = Column(TIMESTAMP, nullable=True)

    episodes = relationship('Episode', order_by=Episode.episode_no, back_populates='bangumi',
                            cascade='all, delete, delete-orphan')

    favorite = relationship('Favorites', back_populates='bangumi', uselist=False)

    watch_progress_list = relationship('WatchProgress', back_populates='bangumi')

    video_files = relationship('VideoFile', order_by=VideoFile.bangumi_id, back_populates='bangumi',
                               cascade='all, delete, delete-orphan')

    cover_image = relationship(Image,
                               foreign_keys=[cover_image_id],
                               primaryjoin='Bangumi.cover_image_id==Image.id')

    # constant of bangumi status
    # A pending bangumi is not started to show on tv yet
    STATUS_PENDING = 0
    # An on air bangumi is currently on air on tv. And not finished yet
    STATUS_ON_AIR = 1
    # A finished bangumi will no longer need to scanned
    STATUS_FINISHED = 2

    # constant of bangumi type
    # anime type
    TYPE_ANIME = 2
    # japanese tv drama series type
    TYPE_JAPANESE_TV_DRAMA_SERIES = 6
