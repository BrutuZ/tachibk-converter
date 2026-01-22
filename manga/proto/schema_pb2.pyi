from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALWAYS_UPDATE: _ClassVar[UpdateStrategy]
    ONLY_FETCH_ONCE: _ClassVar[UpdateStrategy]
ALWAYS_UPDATE: UpdateStrategy
ONLY_FETCH_ONCE: UpdateStrategy

class PreferenceValue(_message.Message):
    __slots__ = ("type", "truevalue")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TRUEVALUE_FIELD_NUMBER: _ClassVar[int]
    type: str
    truevalue: bytes
    def __init__(self, type: _Optional[str] = ..., truevalue: _Optional[bytes] = ...) -> None: ...

class Backup(_message.Message):
    __slots__ = ("backupManga", "backupCategories", "backupSources", "backupPreferences", "backupSourcePreferences", "backupExtensionRepo")
    BACKUPMANGA_FIELD_NUMBER: _ClassVar[int]
    BACKUPCATEGORIES_FIELD_NUMBER: _ClassVar[int]
    BACKUPSOURCES_FIELD_NUMBER: _ClassVar[int]
    BACKUPPREFERENCES_FIELD_NUMBER: _ClassVar[int]
    BACKUPSOURCEPREFERENCES_FIELD_NUMBER: _ClassVar[int]
    BACKUPEXTENSIONREPO_FIELD_NUMBER: _ClassVar[int]
    backupManga: _containers.RepeatedCompositeFieldContainer[BackupManga]
    backupCategories: _containers.RepeatedCompositeFieldContainer[BackupCategory]
    backupSources: _containers.RepeatedCompositeFieldContainer[BackupSource]
    backupPreferences: _containers.RepeatedCompositeFieldContainer[BackupPreference]
    backupSourcePreferences: _containers.RepeatedCompositeFieldContainer[BackupSourcePreferences]
    backupExtensionRepo: _containers.RepeatedCompositeFieldContainer[BackupExtensionRepos]
    def __init__(self, backupManga: _Optional[_Iterable[_Union[BackupManga, _Mapping]]] = ..., backupCategories: _Optional[_Iterable[_Union[BackupCategory, _Mapping]]] = ..., backupSources: _Optional[_Iterable[_Union[BackupSource, _Mapping]]] = ..., backupPreferences: _Optional[_Iterable[_Union[BackupPreference, _Mapping]]] = ..., backupSourcePreferences: _Optional[_Iterable[_Union[BackupSourcePreferences, _Mapping]]] = ..., backupExtensionRepo: _Optional[_Iterable[_Union[BackupExtensionRepos, _Mapping]]] = ...) -> None: ...

class BackupCategory(_message.Message):
    __slots__ = ("name", "order", "id", "flags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    order: int
    id: int
    flags: int
    def __init__(self, name: _Optional[str] = ..., order: _Optional[int] = ..., id: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class BackupChapter(_message.Message):
    __slots__ = ("url", "name", "scanlator", "read", "bookmark", "lastPageRead", "dateFetch", "dateUpload", "chapterNumber", "sourceOrder", "lastModifiedAt", "version")
    URL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCANLATOR_FIELD_NUMBER: _ClassVar[int]
    READ_FIELD_NUMBER: _ClassVar[int]
    BOOKMARK_FIELD_NUMBER: _ClassVar[int]
    LASTPAGEREAD_FIELD_NUMBER: _ClassVar[int]
    DATEFETCH_FIELD_NUMBER: _ClassVar[int]
    DATEUPLOAD_FIELD_NUMBER: _ClassVar[int]
    CHAPTERNUMBER_FIELD_NUMBER: _ClassVar[int]
    SOURCEORDER_FIELD_NUMBER: _ClassVar[int]
    LASTMODIFIEDAT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    url: str
    name: str
    scanlator: str
    read: bool
    bookmark: bool
    lastPageRead: int
    dateFetch: int
    dateUpload: int
    chapterNumber: float
    sourceOrder: int
    lastModifiedAt: int
    version: int
    def __init__(self, url: _Optional[str] = ..., name: _Optional[str] = ..., scanlator: _Optional[str] = ..., read: bool = ..., bookmark: bool = ..., lastPageRead: _Optional[int] = ..., dateFetch: _Optional[int] = ..., dateUpload: _Optional[int] = ..., chapterNumber: _Optional[float] = ..., sourceOrder: _Optional[int] = ..., lastModifiedAt: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class BackupExtensionRepos(_message.Message):
    __slots__ = ("baseUrl", "name", "shortName", "website", "signingKeyFingerprint")
    BASEURL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORTNAME_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    SIGNINGKEYFINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    baseUrl: str
    name: str
    shortName: str
    website: str
    signingKeyFingerprint: str
    def __init__(self, baseUrl: _Optional[str] = ..., name: _Optional[str] = ..., shortName: _Optional[str] = ..., website: _Optional[str] = ..., signingKeyFingerprint: _Optional[str] = ...) -> None: ...

class BackupHistory(_message.Message):
    __slots__ = ("url", "lastRead", "readDuration")
    URL_FIELD_NUMBER: _ClassVar[int]
    LASTREAD_FIELD_NUMBER: _ClassVar[int]
    READDURATION_FIELD_NUMBER: _ClassVar[int]
    url: str
    lastRead: int
    readDuration: int
    def __init__(self, url: _Optional[str] = ..., lastRead: _Optional[int] = ..., readDuration: _Optional[int] = ...) -> None: ...

class BackupManga(_message.Message):
    __slots__ = ("source", "url", "title", "artist", "author", "description", "genre", "status", "thumbnailUrl", "dateAdded", "viewer", "chapters", "categories", "tracking", "favorite", "chapterFlags", "viewer_flags", "history", "updateStrategy", "lastModifiedAt", "favoriteModifiedAt", "excludedScanlators", "version", "notes", "initialized")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    THUMBNAILURL_FIELD_NUMBER: _ClassVar[int]
    DATEADDED_FIELD_NUMBER: _ClassVar[int]
    VIEWER_FIELD_NUMBER: _ClassVar[int]
    CHAPTERS_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    TRACKING_FIELD_NUMBER: _ClassVar[int]
    FAVORITE_FIELD_NUMBER: _ClassVar[int]
    CHAPTERFLAGS_FIELD_NUMBER: _ClassVar[int]
    VIEWER_FLAGS_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    UPDATESTRATEGY_FIELD_NUMBER: _ClassVar[int]
    LASTMODIFIEDAT_FIELD_NUMBER: _ClassVar[int]
    FAVORITEMODIFIEDAT_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEDSCANLATORS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    INITIALIZED_FIELD_NUMBER: _ClassVar[int]
    source: int
    url: str
    title: str
    artist: str
    author: str
    description: str
    genre: _containers.RepeatedScalarFieldContainer[str]
    status: int
    thumbnailUrl: str
    dateAdded: int
    viewer: int
    chapters: _containers.RepeatedCompositeFieldContainer[BackupChapter]
    categories: _containers.RepeatedScalarFieldContainer[int]
    tracking: _containers.RepeatedCompositeFieldContainer[BackupTracking]
    favorite: bool
    chapterFlags: int
    viewer_flags: int
    history: _containers.RepeatedCompositeFieldContainer[BackupHistory]
    updateStrategy: UpdateStrategy
    lastModifiedAt: int
    favoriteModifiedAt: int
    excludedScanlators: _containers.RepeatedScalarFieldContainer[str]
    version: int
    notes: str
    initialized: bool
    def __init__(self, source: _Optional[int] = ..., url: _Optional[str] = ..., title: _Optional[str] = ..., artist: _Optional[str] = ..., author: _Optional[str] = ..., description: _Optional[str] = ..., genre: _Optional[_Iterable[str]] = ..., status: _Optional[int] = ..., thumbnailUrl: _Optional[str] = ..., dateAdded: _Optional[int] = ..., viewer: _Optional[int] = ..., chapters: _Optional[_Iterable[_Union[BackupChapter, _Mapping]]] = ..., categories: _Optional[_Iterable[int]] = ..., tracking: _Optional[_Iterable[_Union[BackupTracking, _Mapping]]] = ..., favorite: bool = ..., chapterFlags: _Optional[int] = ..., viewer_flags: _Optional[int] = ..., history: _Optional[_Iterable[_Union[BackupHistory, _Mapping]]] = ..., updateStrategy: _Optional[_Union[UpdateStrategy, str]] = ..., lastModifiedAt: _Optional[int] = ..., favoriteModifiedAt: _Optional[int] = ..., excludedScanlators: _Optional[_Iterable[str]] = ..., version: _Optional[int] = ..., notes: _Optional[str] = ..., initialized: bool = ...) -> None: ...

class BackupPreference(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: PreferenceValue
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PreferenceValue, _Mapping]] = ...) -> None: ...

class BackupSourcePreferences(_message.Message):
    __slots__ = ("sourceKey", "prefs")
    SOURCEKEY_FIELD_NUMBER: _ClassVar[int]
    PREFS_FIELD_NUMBER: _ClassVar[int]
    sourceKey: str
    prefs: _containers.RepeatedCompositeFieldContainer[BackupPreference]
    def __init__(self, sourceKey: _Optional[str] = ..., prefs: _Optional[_Iterable[_Union[BackupPreference, _Mapping]]] = ...) -> None: ...

class IntPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class LongPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class FloatPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class StringPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class BooleanPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class StringSetPreferenceValue(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, value: _Optional[_Iterable[str]] = ...) -> None: ...

class BackupSource(_message.Message):
    __slots__ = ("name", "sourceId")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCEID_FIELD_NUMBER: _ClassVar[int]
    name: str
    sourceId: int
    def __init__(self, name: _Optional[str] = ..., sourceId: _Optional[int] = ...) -> None: ...

class BackupTracking(_message.Message):
    __slots__ = ("syncId", "libraryId", "mediaIdInt", "trackingUrl", "title", "lastChapterRead", "totalChapters", "score", "status", "startedReadingDate", "finishedReadingDate", "private", "mediaId")
    SYNCID_FIELD_NUMBER: _ClassVar[int]
    LIBRARYID_FIELD_NUMBER: _ClassVar[int]
    MEDIAIDINT_FIELD_NUMBER: _ClassVar[int]
    TRACKINGURL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    LASTCHAPTERREAD_FIELD_NUMBER: _ClassVar[int]
    TOTALCHAPTERS_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STARTEDREADINGDATE_FIELD_NUMBER: _ClassVar[int]
    FINISHEDREADINGDATE_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_FIELD_NUMBER: _ClassVar[int]
    MEDIAID_FIELD_NUMBER: _ClassVar[int]
    syncId: int
    libraryId: int
    mediaIdInt: int
    trackingUrl: str
    title: str
    lastChapterRead: float
    totalChapters: int
    score: float
    status: int
    startedReadingDate: int
    finishedReadingDate: int
    private: bool
    mediaId: int
    def __init__(self, syncId: _Optional[int] = ..., libraryId: _Optional[int] = ..., mediaIdInt: _Optional[int] = ..., trackingUrl: _Optional[str] = ..., title: _Optional[str] = ..., lastChapterRead: _Optional[float] = ..., totalChapters: _Optional[int] = ..., score: _Optional[float] = ..., status: _Optional[int] = ..., startedReadingDate: _Optional[int] = ..., finishedReadingDate: _Optional[int] = ..., private: bool = ..., mediaId: _Optional[int] = ...) -> None: ...
