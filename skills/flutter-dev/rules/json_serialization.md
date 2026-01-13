# JSON Serialization Rules

### Overview
1. Use **json_serializable** for all JSON parsing tasks to ensure type safety and compile-time checking.
2. Avoid manual serialization (`Map<String, dynamic>`) for domain models.
3. Use the `json_annotation` package for defining models and `build_runner` for code generation.

### Setup
1. Add dependencies in `pubspec.yaml`:
   ```yaml
   dependencies:
     json_annotation: ^latest

   dev_dependencies:
     build_runner: ^latest
     json_serializable: ^latest
   ```

### Model Structure
1. Create a class and annotate it with `@JsonSerializable()`.
2. Define the `fromJson` factory constructor.
3. Define the `toJson` method.
4. Include the `part` directive pointing to the generated file (`.g.dart`).

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String name;
  
  // Optional field
  final String? email;

  User({required this.id, required this.name, this.email});

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

### Configuration & Best Practices
1. **Explicit Nulls**: Use `includeIfNull: false` in `@JsonSerializable` if you don't want null values in the JSON output.
2. **Field Renaming**: Use `@JsonKey(name: 'api_field_name')` to map JSON keys that differ from Dart property names (e.g., snake_case to camelCase).
3. **Default Values**: Use `@JsonKey(defaultValue: 'value')` to provide fallbacks for missing keys.
4. **Ignoring Fields**: Use `@JsonKey(includeFromJson: false, includeToJson: false)` for properties that should not be serialized.
5. **Enums**: Annotate enums with `@JsonEnum()` for easier serialization.
   - Use `@JsonValue('value')` on enum members to map to specific JSON values.

### Code Generation
1. Run the builder once:
   ```bash
   dart run build_runner build
   ```
2. Run the builder in watch mode (recommended during development):
   ```bash
   dart run build_runner watch
   ```
3. Resolve conflicting outputs (if needed):
   ```bash
   dart run build_runner build --delete-conflicting-outputs
   ```

### Advanced Usage
1. **Custom Converters**: Use `JsonConverter<T, S>` for complex types that `json_serializable` doesn't handle natively (e.g., `DateTime` formats, custom value objects).
   ```dart
   class MyDateConverter implements JsonConverter<DateTime, int> {
     const MyDateConverter();
     // ... implement fromJson and toJson
   }
   
   @MyDateConverter()
   final DateTime createdAt;
   ```
2. **Generic Classes**: `json_serializable` supports generic classes, but requires extra handling for `fromJsonT` and `toJsonT` functions.

### VS Code Integration
1. Use snippets to generate the boilerplate code quickly.
2. Hide `.g.dart` files in the file explorer if they clutter the view (configure in `.vscode/settings.json`).
