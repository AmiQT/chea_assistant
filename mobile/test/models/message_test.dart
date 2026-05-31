import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/message.dart';

void main() {
  group('Message model', () {
    test('creates user message with required fields', () {
      final msg = Message(
        text: 'Hello AI!',
        isUser: true,
        timestamp: DateTime(2026, 6, 1, 10, 0),
      );

      expect(msg.text, 'Hello AI!');
      expect(msg.isUser, true);
      expect(msg.isThinking, false);
      expect(msg.actionExecuted, false);
      expect(msg.imageData, isNull);
      expect(msg.actions, isNull);
    });

    test('creates AI message with default flags', () {
      final msg = Message(
        text: 'Hi! I am CHEA 🤖',
        isUser: false,
        timestamp: DateTime.now(),
      );

      expect(msg.isUser, false);
      expect(msg.isThinking, false);
      expect(msg.actionExecuted, false);
    });

    test('creates thinking message', () {
      final msg = Message(
        text: 'Thinking... 🤔',
        isUser: false,
        timestamp: DateTime.now(),
        isThinking: true,
      );

      expect(msg.isThinking, true);
    });

    test('creates message with image data', () {
      const fakeBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB';
      final msg = Message(
        text: 'Check this receipt',
        isUser: true,
        timestamp: DateTime.now(),
        imageData: fakeBase64,
      );

      expect(msg.imageData, fakeBase64);
    });

    test('creates message with actions', () {
      final actions = [
        {'type': 'leave_balance_card', 'balances': {'Annual': 14}},
      ];
      final msg = Message(
        text: 'Your leave balance:',
        isUser: false,
        timestamp: DateTime.now(),
        actions: actions,
      );

      expect(msg.actions, isNotNull);
      expect(msg.actions!.length, 1);
      expect(msg.actions![0]['type'], 'leave_balance_card');
    });

    test('actionExecuted is mutable', () {
      final msg = Message(
        text: 'Confirm booking?',
        isUser: false,
        timestamp: DateTime.now(),
      );

      expect(msg.actionExecuted, false);
      msg.actionExecuted = true;
      expect(msg.actionExecuted, true);
    });

    test('timestamp is preserved', () {
      final ts = DateTime(2026, 1, 15, 9, 30, 0);
      final msg = Message(text: 'Hello', isUser: true, timestamp: ts);
      expect(msg.timestamp, ts);
    });
  });
}
