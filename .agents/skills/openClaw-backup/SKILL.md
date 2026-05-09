```markdown
# openClaw-backup Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the `openClaw-backup` TypeScript codebase. You'll learn how to structure files, write imports/exports, follow commit message patterns, and understand the testing approach. This guide is ideal for contributors aiming for consistency and maintainability in this repository.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `userProfile.ts`, `dataManager.test.ts`

### Imports
- Use **relative imports** for modules within the project.
  - Example:
    ```typescript
    import { fetchData } from './apiClient';
    ```

### Exports
- Use **named exports** for all modules.
  - Example:
    ```typescript
    export function processBackup() { ... }
    export const BACKUP_INTERVAL = 60;
    ```

### Commit Messages
- Mostly **freeform** messages.
- Some commits use the `[ImgBot]` prefix for automated image optimizations.
- Average commit message length: ~24 characters.

  Example:
  ```
  [ImgBot] Optimize images
  Add backup scheduler
  ```

## Workflows

### Image Optimization
**Trigger:** When updating or adding images to the repository  
**Command:** `/optimize-images`

1. Add or update image files in the repository.
2. Run the ImgBot or wait for its automated PR.
3. Review the `[ImgBot]` commit for optimized images.
4. Merge the PR if optimizations look correct.

### Adding New Features
**Trigger:** When implementing new functionality  
**Command:** `/add-feature`

1. Create a new TypeScript file using camelCase naming.
2. Use relative imports to include dependencies.
3. Export functions or constants using named exports.
4. Write or update corresponding test files (`*.test.ts`).
5. Commit changes with a clear, concise message.

### Writing Tests
**Trigger:** When adding or updating code that requires testing  
**Command:** `/write-test`

1. Create a test file with the `.test.ts` suffix.
   - Example: `userProfile.test.ts`
2. Implement tests (testing framework is currently unknown; follow existing patterns).
3. Run the test suite to ensure all tests pass.
4. Commit the test file with a descriptive message.

## Testing Patterns

- Test files use the `*.test.ts` naming convention.
- The testing framework is **unknown**; check existing test files for structure and assertions.
- Place test files alongside the modules they test or in a designated test directory.

  Example:
  ```
  userProfile.ts
  userProfile.test.ts
  ```

## Commands
| Command           | Purpose                                      |
|-------------------|----------------------------------------------|
| /optimize-images  | Optimize images using ImgBot                 |
| /add-feature      | Scaffold and add a new feature/module        |
| /write-test       | Create and run tests for new or changed code |
```
