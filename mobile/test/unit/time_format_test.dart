import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

// Tests for time/date formatting logic extracted from UI screens.
// These mirror the logic in room_booking_screen.dart and leave_request_screen.dart.

String formatTime(TimeOfDay time) {
  return '${time.hour.toString().padLeft(2, '0')}:'
      '${time.minute.toString().padLeft(2, '0')}';
}

int timeToMinutes(TimeOfDay time) => time.hour * 60 + time.minute;

String formatDuration(TimeOfDay start, TimeOfDay end) {
  final diff = timeToMinutes(end) - timeToMinutes(start);
  if (diff <= 0) return 'Invalid';
  final hours = diff ~/ 60;
  final mins = diff % 60;
  if (hours > 0 && mins > 0) return '${hours}h ${mins}m';
  if (hours > 0) return '${hours}h';
  return '${mins}m';
}

void main() {
  group('Time formatting (room booking)', () {
    test('formats single-digit hour with leading zero', () {
      expect(formatTime(const TimeOfDay(hour: 9, minute: 0)), '09:00');
    });

    test('formats double-digit hour correctly', () {
      expect(formatTime(const TimeOfDay(hour: 14, minute: 30)), '14:30');
    });

    test('formats midnight as 00:00', () {
      expect(formatTime(const TimeOfDay(hour: 0, minute: 0)), '00:00');
    });

    test('formats 23:59 correctly', () {
      expect(formatTime(const TimeOfDay(hour: 23, minute: 59)), '23:59');
    });

    test('formats minutes with leading zero', () {
      expect(formatTime(const TimeOfDay(hour: 10, minute: 5)), '10:05');
    });
  });

  group('Time to minutes conversion', () {
    test('midnight is 0 minutes', () {
      expect(timeToMinutes(const TimeOfDay(hour: 0, minute: 0)), 0);
    });

    test('1 hour is 60 minutes', () {
      expect(timeToMinutes(const TimeOfDay(hour: 1, minute: 0)), 60);
    });

    test('9:30 is 570 minutes', () {
      expect(timeToMinutes(const TimeOfDay(hour: 9, minute: 30)), 570);
    });

    test('23:59 is 1439 minutes', () {
      expect(timeToMinutes(const TimeOfDay(hour: 23, minute: 59)), 1439);
    });
  });

  group('Duration formatting', () {
    test('1 hour duration shows "1h"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 9, minute: 0),
          const TimeOfDay(hour: 10, minute: 0),
        ),
        '1h',
      );
    });

    test('90 minute duration shows "1h 30m"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 9, minute: 0),
          const TimeOfDay(hour: 10, minute: 30),
        ),
        '1h 30m',
      );
    });

    test('30 minute duration shows "30m"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 9, minute: 0),
          const TimeOfDay(hour: 9, minute: 30),
        ),
        '30m',
      );
    });

    test('invalid duration (end before start) shows "Invalid"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 10, minute: 0),
          const TimeOfDay(hour: 9, minute: 0),
        ),
        'Invalid',
      );
    });

    test('same start and end shows "Invalid"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 10, minute: 0),
          const TimeOfDay(hour: 10, minute: 0),
        ),
        'Invalid',
      );
    });

    test('2 hours exact shows "2h"', () {
      expect(
        formatDuration(
          const TimeOfDay(hour: 14, minute: 0),
          const TimeOfDay(hour: 16, minute: 0),
        ),
        '2h',
      );
    });
  });

  group('Leave day calculation', () {
    test('same day leave is 1 day', () {
      final start = DateTime(2026, 8, 1);
      final end = DateTime(2026, 8, 1);
      final days = end.difference(start).inDays + 1;
      expect(days, 1);
    });

    test('3 day leave is 3 days', () {
      final start = DateTime(2026, 8, 1);
      final end = DateTime(2026, 8, 3);
      final days = end.difference(start).inDays + 1;
      expect(days, 3);
    });

    test('end before start gives negative difference', () {
      final start = DateTime(2026, 8, 10);
      final end = DateTime(2026, 8, 5);
      final days = end.difference(start).inDays + 1;
      expect(days, isNegative);
    });

    test('full week (Mon-Fri) is 5 days', () {
      final start = DateTime(2026, 8, 3);  // Monday
      final end = DateTime(2026, 8, 7);    // Friday
      final days = end.difference(start).inDays + 1;
      expect(days, 5);
    });
  });

  group('Chat ask-for-date detection', () {
    // Mirror of _asksForDate() logic in chat_screen.dart
    bool asksForDate(String text) {
      final lower = text.toLowerCase();
      const keywords = [
        'tarikh', 'date', 'bila', 'when', 'start date', 'end date',
        'tarikh mula', 'tarikh tamat', 'pilih tarikh', 'masukkan tarikh',
        'enter date', 'what date', 'which date',
      ];
      return keywords.any((k) => lower.contains(k));
    }

    test('detects "tarikh" keyword', () {
      expect(asksForDate('Bila tarikh cuti kau?'), isTrue);
    });

    test('detects "date" keyword', () {
      expect(asksForDate('What is the start date?'), isTrue);
    });

    test('detects "bila" keyword', () {
      expect(asksForDate('Cuti bila?'), isTrue);
    });

    test('normal greeting is not a date question', () {
      expect(asksForDate('Hai! Aku CHEA 🤖'), isFalse);
    });

    test('leave balance query is not a date question', () {
      expect(asksForDate('Berapa baki cuti aku?'), isFalse);
    });

    test('is case insensitive', () {
      expect(asksForDate('What DATE is your vacation?'), isTrue);
    });
  });
}
