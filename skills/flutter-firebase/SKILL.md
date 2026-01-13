---
name: flutter-firebase
description: Expert guidance for Firebase integration in Flutter apps. Use when setting up Firebase, implementing authentication, using Cloud Firestore, Cloud Storage, Cloud Functions, FCM push notifications, Analytics, or any other Firebase services. Provides access to detailed rules for all major Firebase Flutter plugins.
---

# Flutter Firebase Skill

## Overview

This Skill provides expert guidance for integrating Firebase services into Flutter applications. It references comprehensive documentation for each Firebase service.

**Before starting any Firebase integration**: Always read the corresponding `.md` file in the current directory for detailed, official documentation-based guidance.

## Firebase Services Reference

When working with specific Firebase services, **read the detailed documentation**:

| Service                | Read This                          | When to Use                                      |
| ---------------------- | ---------------------------------- | ------------------------------------------------ |
| FlutterFire Setup      | `./flutterfire_configure.md`      | Initial Firebase setup, configuration, flavors   |
| Authentication         | `./firebase_auth.md`              | Email/password, social auth, session management  |
| Cloud Firestore        | `./cloud_firestore.md`            | NoSQL database, real-time data, queries          |
| Cloud Storage          | `./firebase_storage.md`           | File uploads, images, document storage           |
| Cloud Functions        | `./cloud_functions.md`            | Server-side logic, callable functions            |
| Cloud Messaging (FCM)  | `./firebase_messaging.md`         | Push notifications, message handling             |
| Analytics              | `./firebase_analytics.md`         | Event tracking, user properties, analytics       |
| App Check              | `./firebase_app_check.md`         | App integrity protection, abuse prevention       |
| Crashlytics            | `./firebase_crashlytics.md`       | Crash reporting, error tracking                  |
| Realtime Database      | `./firebase_database.md`          | Real-time sync database (legacy)                 |
| Remote Config          | `./firebase_remote_config.md`     | Remote configuration, feature flags              |
| In-App Messaging       | `./firebase_in_app_messaging.md`  | In-app messages, user engagement                 |
| Firebase AI            | `./firebase_ai.md`                | AI/ML features, generative AI                    |
| Data Connect           | `./firebase_data_connect.md`      | Firebase Data Connect for managed backends       |

## Quick Start: Firebase Setup

Copy this checklist for new projects:

```
Firebase Setup Progress:
- [ ] 1. Install Firebase CLI: npm install -g firebase-tools
- [ ] 2. Login: firebase login
- [ ] 3. Install FlutterFire CLI: dart pub global activate flutterfire_cli
- [ ] 4. Run: flutterfire configure (from project directory)
- [ ] 5. Add firebase_core: flutter pub add firebase_core
- [ ] 6. Initialize in main.dart
- [ ] 7. Add specific Firebase services as needed
- [ ] 8. Test on all target platforms
```

**For detailed setup instructions, read `./flutterfire_configure.md`**

## Common Workflows

### Workflow: Adding Authentication

```
Authentication Setup:
- [ ] 1. Enable providers in Firebase Console
- [ ] 2. Add firebase_auth plugin: flutter pub add firebase_auth
- [ ] 3. Read ./firebase_auth.md for your auth method
- [ ] 4. Implement auth state listener
- [ ] 5. Handle user sessions
```

### Workflow: Cloud Firestore Database

```
Firestore Setup:
- [ ] 1. Add cloud_firestore plugin: flutter pub add cloud_firestore
- [ ] 2. Read ./cloud_firestore.md for data modeling
- [ ] 3. Configure security rules in Firebase Console
- [ ] 4. Set up indexes for queries
- [ ] 5. Implement CRUD operations
```

### Workflow: Push Notifications (FCM)

```
FCM Setup:
- [ ] 1. Add firebase_messaging plugin: flutter pub add firebase_messaging
- [ ] 2. Read ./firebase_messaging.md for platform setup
- [ ] 3. Configure APNs key (iOS) / FCM Server key (Android)
- [ ] 4. Request notification permissions
- [ ] 5. Set up message handlers (foreground/background)
```

## Code Patterns

### Firebase Initialization

```dart
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}
```

### Authentication State Listener

```dart
FirebaseAuth.instance.authStateChanges().listen((User? user) {
  if (user == null) {
    // User is signed out
  } else {
    // User is signed in
  }
});
```

### Firestore Read Operations

```dart
final db = FirebaseFirestore.instance;

// Get a document
final doc = await db.collection('users').doc(userId).get();

// Query with filters
final snapshot = await db.collection('users')
    .where('age', isGreaterThan: 18)
    .get();

// Real-time updates
db.collection('users').snapshots().listen((event) {
  for (var change in event.docChanges) {
    // Handle changes
  }
});
```

### File Upload to Storage

```dart
final storage = FirebaseStorage.instance;
final ref = storage.ref().child('uploads/$fileName');

final uploadTask = ref.putFile(file);
final snapshot = await uploadTask;
final downloadUrl = await snapshot.ref.getDownloadURL();
```

### Cloud Function Call

```dart
final result = await FirebaseFunctions.instance
    .httpsCallable('functionName')
    .call({'param': 'value'});

final responseData = result.data;
```

## Platform-Specific Notes

### iOS
- Requires Firebase configuration file (GoogleService-Info.plist)
- APNs key required for FCM
- Keychain Sharing capability needed for some services

### Android
- Requires google-services.json configuration file
- Minimum SDK: API level 19 (KitKat)
- Google Play services required for most features

### Web
- Uses web configuration from Firebase Console
- VAPID key required for FCM web push
- Service worker required for FCM background messages

## Security Best Practices

1. **Always use Firebase Security Rules** for Firestore, Storage, and Database
2. **Never store sensitive data** in client-side code
3. **Use Firebase Authentication** to control data access
4. **Validate user input** before sending to Firebase
5. **Enable App Check** for production apps to prevent abuse

## Common Pitfalls

❌ **Don't**: Forget to call `WidgetsFlutterBinding.ensureInitialized()` before Firebase initialization
❌ **Don't**: Modify `firebase_options.dart` manually (it's auto-generated)
❌ **Don't**: Use Firebase services before initialization completes
❌ **Don't**: Ignore error handling for async Firebase operations
❌ **Don't**: Store large files directly in Firestore (use Storage instead)

## Troubleshooting

**Issue**: "FirebaseException: No Firebase App '[DEFAULT]' has been created"
→ Ensure `Firebase.initializeApp()` is called before any Firebase service

**Issue**: Platform not found after adding new Firebase plugin
→ Run `flutterfire configure` again for the new platform

**Issue**: FCM not working on iOS
→ Verify APNs key is uploaded and matches bundle ID

**Issue**: Firestore queries failing
→ Check if composite indexes are needed (error message will provide link)

## Reference

- [FlutterFire Documentation](https://firebase.flutter.dev/docs/overview/)
- [Firebase Console](https://console.firebase.google.com/)
- [evanca/flutter-ai-rules](https://github.com/evanca/flutter-ai-rules)
