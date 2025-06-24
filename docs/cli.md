# CLI Reference

## Main Command

```
Usage: root [OPTIONS] COMMAND [ARGS]...                                       
                                                                               
 Client tool for the ESA synthetic scene generator service DTE-S2GOS.          
                                                                               
 The tool provides commands for managing processing request templates,         
 processing requests, processing jobs, and gets processing results.            
 You can use shorter command name aliases, e.g., use command name "vr" instead 
 of "validate-request", or "lt" instead of "list-templates".                   
                                                                               
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --help          Show this message and exit.                                 │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Commands ──────────────────────────────────────────────────────────────────┐
│ configure          Configure the S2GOS client.                              │
│ get-template       Get a processing request template.                       │
│ list-templates     List available processing request templates.             │
│ validate-request   Validate a processing request.                           │
│ submit-request     Submit a processing request.                             │
│ cancel-jobs        Cancel running processing jobs.                          │
│ poll-jobs          Poll the status of processing jobs.                      │
│ get-results        Get processing results.                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Commands

### `configure`

```
Usage: root configure [OPTIONS]                                               
                                                                               
 Configure the S2GOS client.                                                   
                                                                               
                                                                               
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --user         TEXT  [default: None]                                        │
│ --token        TEXT  [default: None]                                        │
│ --url          TEXT  [default: None]                                        │
│ --help               Show this message and exit.                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `get-template`

```
Usage: root get-template [OPTIONS] TEMPLATE_NAME                              
                                                                               
 Get a processing request template.                                            
                                                                               
                                                                               
┌─ Arguments ─────────────────────────────────────────────────────────────────┐
│ *    template_name      TEXT  [default: None] [required]                    │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --request        TEXT  [default: s2gos-request.yaml]                        │
│ --help                 Show this message and exit.                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `list-templates`

```
Usage: root list-templates [OPTIONS]                                          
                                                                               
 List available processing request templates.                                  
                                                                               
                                                                               
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --help          Show this message and exit.                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `validate-request`

```
Usage: root validate-request [OPTIONS]                                        
                                                                               
 Validate a processing request.                                                
                                                                               
                                                                               
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --name        TEXT  [default: s2gos-request.yaml]                           │
│ --help              Show this message and exit.                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `submit-request`

```
Usage: root submit-request [OPTIONS]                                          
                                                                               
 Submit a processing request.                                                  
                                                                               
                                                                               
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --name        TEXT  [default: s2gos-request.yaml]                           │
│ --help              Show this message and exit.                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `cancel-jobs`

```
Usage: root cancel-jobs [OPTIONS] JOB_IDS...                                  
                                                                               
 Cancel running processing jobs.                                               
                                                                               
                                                                               
┌─ Arguments ─────────────────────────────────────────────────────────────────┐
│ *    job_ids      JOB_IDS...  [default: None] [required]                    │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --help          Show this message and exit.                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `poll-jobs`

```
Usage: root poll-jobs [OPTIONS] JOB_IDS...                                    
                                                                               
 Poll the status of processing jobs.                                           
                                                                               
                                                                               
┌─ Arguments ─────────────────────────────────────────────────────────────────┐
│ *    job_ids      JOB_IDS...  [default: None] [required]                    │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --help          Show this message and exit.                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### `get-results`

```
Usage: root get-results [OPTIONS] JOB_IDS...                                  
                                                                               
 Get processing results.                                                       
                                                                               
                                                                               
┌─ Arguments ─────────────────────────────────────────────────────────────────┐
│ *    job_ids      JOB_IDS...  [default: None] [required]                    │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --help          Show this message and exit.                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```
