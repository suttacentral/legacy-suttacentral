ALTER TABLE collection_language ADD COLUMN language_code CHAR(2) NOT NULL;
UPDATE collection_language SET language_code = 'pi' WHERE collection_language_abbrev_name = 'Pali';
UPDATE collection_language SET language_code = 'zh' WHERE collection_language_abbrev_name = 'Chin';
UPDATE collection_language SET language_code = 'bo' WHERE collection_language_abbrev_name = 'Tib';
UPDATE collection_language SET language_code = 'sa' WHERE collection_language_abbrev_name = 'Skt';
UPDATE collection_language SET language_code = 'en' WHERE collection_language_abbrev_name = 'Oth';
UPDATE sutta SET collection_language_id = 3 WHERE collection_language_id = 7;
