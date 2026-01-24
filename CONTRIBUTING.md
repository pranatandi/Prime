# Contributing to Prime Weighing System

Thank you for your interest in contributing to the Prime Palm Fruit Weighing System! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (PHP version, database, browser)
- Screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- Clear description of the enhancement
- Use cases and benefits
- Any potential implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/pranatandi/Prime.git
   cd Prime
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow PSR-12 coding standards
   - Add tests for new features
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for UI changes

## Development Guidelines

### Code Style

- Follow PSR-12 coding standards
- Use meaningful variable and method names
- Add comments for complex logic
- Keep methods small and focused

**Run linter:**
```bash
./vendor/bin/pint
```

### Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage

**Run tests:**
```bash
php artisan test
```

### Database Changes

- Create migrations for schema changes
- Update seeders if needed
- Test migrations both up and down

### Documentation

- Update README.md for new features
- Update API.md for new endpoints
- Add inline documentation for complex code

## Project Structure

```
Prime/
├── app/
│   ├── Http/Controllers/  # Controllers
│   ├── Models/            # Eloquent models
│   ├── Services/          # Business logic
│   └── Traits/            # Reusable traits
├── database/
│   ├── migrations/        # Database migrations
│   ├── seeders/           # Data seeders
│   └── factories/         # Model factories
├── resources/
│   └── views/             # Blade templates
├── tests/
│   ├── Feature/           # Feature tests
│   └── Unit/              # Unit tests
└── public/
    ├── sw.js              # Service Worker
    └── manifest.json      # PWA Manifest
```

## Feature Development Workflow

1. **Create migration** (if database changes needed)
   ```bash
   php artisan make:migration create_table_name
   ```

2. **Create model**
   ```bash
   php artisan make:model ModelName
   ```

3. **Create controller**
   ```bash
   php artisan make:controller ControllerName --resource
   ```

4. **Create views** in `resources/views/`

5. **Add routes** in `routes/web.php`

6. **Write tests**
   ```bash
   php artisan make:test FeatureTest
   ```

7. **Run tests**
   ```bash
   php artisan test
   ```

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat: Add export to Excel functionality
fix: Correct net weight calculation
docs: Update installation instructions
test: Add tests for supplier deletion
```

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows PSR-12 standards
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commits are clean and descriptive
- [ ] Code is self-documented or has comments

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the "question" label
- Contact the maintainers
- Review existing issues and PRs for examples

## License

By contributing to Prime, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project's release notes and documentation.

Thank you for contributing to Prime Weighing System! 🎉
