# Client CLI Reference

## Main Command

```
Usage: s2gos-client [OPTIONS] COMMAND [ARGS]...                                                                                                                
                                                                                                                                                                
 Client tool for the S2GOS service.                                                                                                                             
                                                                                                                                                                
 The tool provides commands for managing processing request templates, processing requests, processing jobs, and gets processing results.                       
 You can use shorter command name aliases, e.g., use command name "vr" for "validate-request", or "lp" for "list-processes".                                    
                                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version                     Show version and exit                                                                                                          │
│ --install-completion          Install completion for the current shell.                                                                                      │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                               │
│ --help                        Show this message and exit.                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ configure          Configure the client tool.                                                                                                                │
│ list-processes     List available processes.                                                                                                                 │
│ get-process        Get process details.                                                                                                                      │
│ validate-request   Validate a processing request.                                                                                                            │
│ execute-process    Execute a process.                                                                                                                        │
│ list-jobs          List all jobs.                                                                                                                            │
│ get-job            Get job details.                                                                                                                          │
│ dismiss-job        Cancel a running or delete a finished job.                                                                                                │
│ get-job-results    Get job results.                                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Commands

### `configure`

```
Usage: s2gos-client configure [OPTIONS]                                                                                                                        
                                                                                                                                                                
 Configure the client tool.                                                                                                                                     
                                                                                                                                                                
                                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --user         TEXT  [default: None]                                                                                                                         │
│ --token        TEXT  [default: None]                                                                                                                         │
│ --url          TEXT  [default: None]                                                                                                                         │
│ --help               Show this message and exit.                                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `list-processes`

```
Usage: s2gos-client list-processes [OPTIONS]                                                                                                                   
                                                                                                                                                                
 List available processes.                                                                                                                                      
                                                                                                                                                                
                                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `get-process`

```
Usage: s2gos-client get-process [OPTIONS] PROCESS_ID                                                                                                           
                                                                                                                                                                
 Get process details.                                                                                                                                           
                                                                                                                                                                
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    process_id      TEXT  Process identifier [default: None] [required]                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `validate-request`

```
Usage: s2gos-client validate-request [OPTIONS] [PROCESS_ID] [NAME=VALUE]...                                                                                    
                                                                                                                                                                
 Validate a processing request.                                                                                                                                 
                                                                                                                                                                
 The `--request` option and the `process_id` argument are mutually exclusive.                                                                                   
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   process_id      [PROCESS_ID]     Process identifier [default: None]                                                                                        │
│   parameters      [NAME=VALUE]...  Parameters [default: None]                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --request  -r      PATH                Processing request file [default: None]                                                                               │
│ --format   -f      [simple|json|yaml]  Output format [default: yaml]                                                                                         │
│ --help                                 Show this message and exit.                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `execute-process`

```
Usage: s2gos-client execute-process [OPTIONS] [PROCESS_ID] [NAME=VALUE]...                                                                                     
                                                                                                                                                                
 Execute a process.                                                                                                                                             
                                                                                                                                                                
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   process_id      [PROCESS_ID]     Process identifier [default: None]                                                                                        │
│   parameters      [NAME=VALUE]...  Parameters [default: None]                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --request  -r      PATH                Processing request file [default: None]                                                                               │
│ --config   -c      PATH                Client configuration file [default: None]                                                                             │
│ --format   -f      [simple|json|yaml]  Output format [default: yaml]                                                                                         │
│ --help                                 Show this message and exit.                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `list-jobs`

```
Usage: s2gos-client list-jobs [OPTIONS]                                                                                                                        
                                                                                                                                                                
 List all jobs.                                                                                                                                                 
                                                                                                                                                                
                                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `get-job`

```
Usage: s2gos-client get-job [OPTIONS] JOB_ID                                                                                                                   
                                                                                                                                                                
 Get job details.                                                                                                                                               
                                                                                                                                                                
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    job_id      TEXT  Job identifier [default: None] [required]                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `dismiss-job`

```
Usage: s2gos-client dismiss-job [OPTIONS] JOB_ID                                                                                                               
                                                                                                                                                                
 Cancel a running or delete a finished job.                                                                                                                     
                                                                                                                                                                
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    job_id      TEXT  Job identifier [default: None] [required]                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `get-job-results`

```
Usage: s2gos-client get-job-results [OPTIONS] JOB_ID                                                                                                           
                                                                                                                                                                
 Get job results.                                                                                                                                               
                                                                                                                                                                
                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    job_id      TEXT  Job identifier [default: None] [required]                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config  -c      PATH                Client configuration file [default: None]                                                                              │
│ --format  -f      [simple|json|yaml]  Output format [default: yaml]                                                                                          │
│ --help                                Show this message and exit.                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
