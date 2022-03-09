# CTF - Complementary Testing Framework

    ( commit once, measure nonce )

> CTF is an collection of various utilities such as:

## [`Datastore`, `DatastoreProvider` and `DatastoreSubscriber`](./lib/datastore/datastore.py)
 
Which together creates useful utility to store branched data structures

Also implements SqliteDatastore for reading and writing to sql table without need for writing sql code itself.

## [`LoggerBuilder`](./lib/logging/logger_gen.py#L9)

Creates a logger via inherit python logging system with full setup.

## [`Template`](./lib/templating/template.py#L158) 

As of Python 3.10 provides similar functionaly as dataclasses, but with different implementation. Provides facility to store data in different format that when using them directly - implements getter and setter data formatting and easy way to access stored data as json dump.

## [`Webapi`](./lib/webapi/webapi.py#L23) 

Wraps selenium webapi to provide support for creation of POM elements such as: `Page` and `Container`. Those are treated as `DatastoreSubscriber` to the passed webapi, which serves as `RootDatastoreProvider`.  

---  
  
    
> CFT also provides few helper tools:  

## [Project directory generator](./tools/project_dir_gen.py)

Generates project directory with underlaying subdirectories based on available configuration from templates.

### [Task markdown generator](./tools/task_md.py)

Generates project task markdown based on passed template. Provides title, description, preview of template, gained task score, summary of pytest results.