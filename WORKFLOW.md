# 🔄 RPG DM Agent - Safe Update Workflow

## 📋 Overview
This document outlines the safe workflow for updating the RPG DM Agent project, ensuring backups are created and code is reviewed before committing to GitHub.

## 🛡️ Safety First Principles
1. **Always create backups** before making any changes
2. **Review code thoroughly** before committing
3. **Test functionality** after updates
4. **Commit only when everything is working**

## 📁 Backup System

### Automatic Backup Creation
Before any file modification, a timestamped backup is automatically created in the `backups/` directory.

**Backup Format:** `filename_backup_YYYYMMDD_HHMMSS.py`

### Manual Backup Creation
```bash
# Create backup of specific file
python backup_script.py

# Or create backup of all critical files
python -c "from backup_script import backup_critical_files; backup_critical_files()"
```

## 🔍 Review Process

### Automated Review Script
The `review_and_commit.py` script performs comprehensive checks:

1. **Python Syntax Check** - Validates all Python files
2. **Import Validation** - Ensures all imports are valid
3. **Streamlit Compatibility** - Checks Streamlit integration
4. **Git Status** - Reviews changes before commit

### Running the Review
```bash
python review_and_commit.py
```

## 🚀 Complete Workflow

### Step 1: Create Backup
```bash
python backup_script.py
```

### Step 2: Make Changes
- Edit files as needed
- Test functionality locally
- Ensure all features work correctly

### Step 3: Run Review
```bash
python review_and_commit.py
```

### Step 4: Commit (if review passes)
The review script will automatically:
- Stage all changes
- Commit with your message
- Push to GitHub

## 📝 File Structure

```
RPG_DM_Agent/
├── backups/                 # Backup files (excluded from git)
│   ├── streamlit_ui_backup_20251023_011428.py
│   └── ...
├── backup_script.py         # Backup creation script
├── review_and_commit.py     # Review and commit script
├── WORKFLOW.md             # This workflow documentation
└── .gitignore              # Excludes backup files
```

## ⚠️ Important Notes

### Backup Files
- Backup files are **excluded from Git** via `.gitignore`
- Backups are stored locally only
- Keep backups for rollback purposes

### Review Requirements
- **All syntax errors must be fixed** before commit
- **All import errors must be resolved** before commit
- **Streamlit compatibility must be maintained** before commit

### Emergency Rollback
If issues occur after commit:
1. Check `backups/` directory for recent backup
2. Copy backup file over current file
3. Test functionality
4. Commit rollback if needed

## 🎯 Best Practices

### Before Making Changes
1. ✅ Create backup using `backup_script.py`
2. ✅ Review current code structure
3. ✅ Plan changes carefully

### During Development
1. ✅ Test changes frequently
2. ✅ Check for syntax errors
3. ✅ Validate imports
4. ✅ Test Streamlit functionality

### Before Committing
1. ✅ Run `review_and_commit.py`
2. ✅ Fix any errors found
3. ✅ Test final functionality
4. ✅ Only commit when review passes

### After Committing
1. ✅ Verify GitHub repository updated
2. ✅ Test deployed functionality
3. ✅ Keep backup files for reference

## 🔧 Troubleshooting

### Common Issues

**Syntax Errors:**
- Check Python syntax carefully
- Use proper indentation
- Validate all brackets and quotes

**Import Errors:**
- Ensure all required packages are installed
- Check import paths
- Verify module availability

**Streamlit Errors:**
- Test Streamlit compatibility
- Check session state usage
- Validate widget configurations

**Git Issues:**
- Ensure working directory is clean
- Check git status before committing
- Verify GitHub repository access

## 📞 Support

If you encounter issues:
1. Check backup files for rollback
2. Review error messages carefully
3. Test changes incrementally
4. Use the review script to identify problems

---

**Remember: Safety first! Always backup before updating, and only commit when everything is working perfectly.** 🛡️
