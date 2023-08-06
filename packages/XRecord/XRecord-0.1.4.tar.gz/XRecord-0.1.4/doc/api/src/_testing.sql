CREATE TABLE author ( id integer PRIMARY KEY autoincrement, name text);
CREATE TABLE blog_entry (id integer PRIMARY KEY autoincrement,
       author integer constraint be_1 REFERENCES author (id) ON DELETE cascade, title text, content text, ts timestamp );
CREATE TABLE category (id integer PRIMARY KEY autoincrement, name text );
CREATE TABLE entry_category (
       entry integer constraint ce_1 REFERENCES blog_entry(id) ON DELETE cascade,
       category integer constraint ce_2 REFERENCES category(id) ON DELETE cascade, PRIMARY KEY (entry, category) );

-- Drop Trigger
DROP TRIGGER fki_blog_entry_author_author_id;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_blog_entry_author_author_id
BEFORE INSERT ON [blog_entry]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "blog_entry" violates foreign key constraint "fki_blog_entry_author_author_id"')
  WHERE NEW.author IS NOT NULL AND (SELECT id FROM author WHERE id = NEW.author) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fku_blog_entry_author_author_id;

-- Foreign key preventing update
CREATE TRIGGER fku_blog_entry_author_author_id
BEFORE UPDATE ON [blog_entry] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "blog_entry" violates foreign key constraint "fku_blog_entry_author_author_id"')
      WHERE NEW.author IS NOT NULL AND (SELECT id FROM author WHERE id = NEW.author) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fkdc_blog_entry_author_author_id;

-- Cascading Delete
CREATE TRIGGER fkdc_blog_entry_author_author_id
BEFORE DELETE ON author
FOR EACH ROW BEGIN 
    DELETE FROM blog_entry WHERE blog_entry.author = OLD.id;
END;

-- Drop Trigger
DROP TRIGGER fki_entry_category_entry_blog_entry_id;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_entry_category_entry_blog_entry_id
BEFORE INSERT ON [entry_category]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "entry_category" violates foreign key constraint "fki_entry_category_entry_blog_entry_id"')
  WHERE NEW.entry IS NOT NULL AND (SELECT id FROM blog_entry WHERE id = NEW.entry) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fku_entry_category_entry_blog_entry_id;

-- Foreign key preventing update
CREATE TRIGGER fku_entry_category_entry_blog_entry_id
BEFORE UPDATE ON [entry_category] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "entry_category" violates foreign key constraint "fku_entry_category_entry_blog_entry_id"')
      WHERE NEW.entry IS NOT NULL AND (SELECT id FROM blog_entry WHERE id = NEW.entry) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fkdc_entry_category_entry_blog_entry_id;

-- Cascading Delete
CREATE TRIGGER fkdc_entry_category_entry_blog_entry_id
BEFORE DELETE ON blog_entry
FOR EACH ROW BEGIN 
    DELETE FROM entry_category WHERE entry_category.entry = OLD.id;
END;

-- Drop Trigger
DROP TRIGGER fki_entry_category_category_category_id;

-- Foreign Key Preventing insert
CREATE TRIGGER fki_entry_category_category_category_id
BEFORE INSERT ON [entry_category]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "entry_category" violates foreign key constraint "fki_entry_category_category_category_id"')
  WHERE NEW.category IS NOT NULL AND (SELECT id FROM category WHERE id = NEW.category) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fku_entry_category_category_category_id;

-- Foreign key preventing update
CREATE TRIGGER fku_entry_category_category_category_id
BEFORE UPDATE ON [entry_category] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "entry_category" violates foreign key constraint "fku_entry_category_category_category_id"')
      WHERE NEW.category IS NOT NULL AND (SELECT id FROM category WHERE id = NEW.category) IS NULL;
END;

-- Drop Trigger
DROP TRIGGER fkdc_entry_category_category_category_id;

-- Cascading Delete
CREATE TRIGGER fkdc_entry_category_category_category_id
BEFORE DELETE ON category
FOR EACH ROW BEGIN 
    DELETE FROM entry_category WHERE entry_category.category = OLD.id;
END;
