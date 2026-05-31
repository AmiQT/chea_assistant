/// ==============================================================================
/// MODULE: Config
/// ==============================================================================
///
/// Environment configuration for API base URL.
/// Automatically detects platform and sets appropriate localhost address.
/// ==============================================================================
library;

import 'dart:io';
import 'package:flutter/foundation.dart';

class Config {
  // Debug mode → localhost. Release mode → API_BASE_URL env var.
  // Set via: flutter run --dart-define=API_BASE_URL=https://your-backend.com
  static const String _prodUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static bool get isLocal => kDebugMode;

  static String get baseUrl {
    if (isLocal) {
      if (Platform.isAndroid) return 'http://10.0.2.2:8000';
      return 'http://localhost:8000';
    }
    return _prodUrl;
  }

  static const String testUserId = "11111111-1111-1111-1111-111111111111";
}
