import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/config.dart';

void main() {
  group('Config', () {
    test('isLocal returns true in test mode', () {
      expect(Config.isLocal, isA<bool>());
    });

    test('testUserId is a valid UUID format', () {
      const uid = Config.testUserId;
      expect(uid, '11111111-1111-1111-1111-111111111111');
      expect(uid.split('-').length, 5);
    });

    test('baseUrl is not empty', () {
      expect(Config.baseUrl, isNotEmpty);
    });

    test('baseUrl starts with http', () {
      expect(Config.baseUrl, startsWith('http'));
    });

    test('baseUrl contains localhost when isLocal is true', () {
      if (Config.isLocal) {
        expect(
          Config.baseUrl.contains('localhost') ||
              Config.baseUrl.contains('10.0.2.2'),
          isTrue,
        );
      }
    });
  });
}
