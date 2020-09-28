<template>
  <div>
    <!-- <textarea type="text" v-model="keyboardText"></textarea> -->
    <ul class="keyboard">
      <li
        v-for="(key,index) in keyList"
        :key="index"
        :class="{delete: key === 'Delete', tab: key === 'Tab', capslock: key === 'Caps', 
		 enter: key === 'Enter', shift: key === 'Shift', space: key === 'Space', 
		 shifted: (key === 'Shift') && hasShifted, capsed: (key === 'Caps') && hasCapsed }"
        v-text="key"
        @click="clickKey(key)"
      >{{key}}</li>
    </ul>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      keyboardText: '',
      keyList: [],
      normalKeyList: [],
      shiftedKeyList: [],
      capsedKeyList: [],
      hasShifted: false,
      hasCapsed: false,
    }
  },
  created() {
    let normalKeyList = [
        '`',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '0',
        '-',
        '=',
        'Delete',
        'Tab',
        'q',
        'w',
        'e',
        'r',
        't',
        'y',
        'u',
        'i',
        'o',
        'p',
        '[',
        ']',
        '\\',
        'Caps',
        'a',
        's',
        'd',
        'f',
        'g',
        'h',
        'j',
        'k',
        'l',
        ';',
        "'",
        'Enter',
        'Shift',
        'z',
        'x',
        'c',
        'v',
        'b',
        'n',
        'm',
        ',',
        '.',
        '/',
        'Shift',
        'Space',
      ],
      shiftedKeyList = [
        '~',
        '!',
        '@',
        '#',
        '$',
        '%',
        '^',
        '&',
        '*',
        '(',
        ')',
        '_',
        '+',
        'Delete',
        'Tab',
        'Q',
        'W',
        'E',
        'R',
        'T',
        'Y',
        'U',
        'I',
        'O',
        'P',
        '{',
        '}',
        '|',
        'Caps',
        'A',
        'S',
        'D',
        'F',
        'G',
        'H',
        'J',
        'K',
        'L',
        ':',
        '"',
        'Enter',
        'Shift',
        'Z',
        'X',
        'C',
        'V',
        'B',
        'N',
        'M',
        '<',
        '>',
        '?',
        'Shift',
        'Space',
      ],
      capsedKeyList = [
        '`',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '0',
        '-',
        '=',
        'Delete',
        'Tab',
        'Q',
        'W',
        'E',
        'R',
        'T',
        'Y',
        'U',
        'I',
        'O',
        'P',
        '[',
        ']',
        '\\',
        'Caps',
        'A',
        'S',
        'D',
        'F',
        'G',
        'H',
        'J',
        'K',
        'L',
        ';',
        "'",
        'Enter',
        'Shift',
        'Z',
        'X',
        'C',
        'V',
        'B',
        'N',
        'M',
        ',',
        '.',
        '/',
        'Shift',
        'Space',
      ]
    this.keyList = this.normalKeyList = normalKeyList
    this.shiftedKeyList = shiftedKeyList
    this.capsedKeyList = capsedKeyList
  },
  methods: {
    clickKey(key) {
      switch (key) {
        case 'Delete':
          let kbt = this.keyboardText
          this.keyboardText = kbt.length
            ? kbt.substring(0, kbt.length - 1)
            : kbt
          break
        case 'Tab':
          // this.keyboardText += "\t";
          this.keyboardText += ''
          break
        case 'Enter':
          // this.keyboardText += "ent";
          this.$emit('submit')
          break
        case 'Space':
          this.keyboardText += ''
          break
        case 'Caps':
          this.hasCapsed = !this.hasCapsed
          this.keyList = this.hasCapsed
            ? this.capsedKeyList
            : this.normalKeyList
          break
        case 'Shift':
          this.hasShifted = !this.hasShifted
          this.keyList = this.hasShifted
            ? this.shiftedKeyList
            : this.normalKeyList
          break
        default:
          this.keyboardText += key.toString()
          break
      }
      this.$emit('sendtext', this.keyboardText)
    },
  },
}
</script>

<style scoped>
/* textarea {
  display: block;
  width: 100%;
  min-height: 100px;
  padding: 0;
  margin: 20px 0;
  font-size: 16px;
} */
.keyboard {
  position: absolute;
  top: 110%;
  left: 50%;
  transform: translateX(-50%);

  width: 688px;
  margin: 0;
  padding: 0;
  list-style: none;
  user-select: none;
}

.keyboard li {
  float: left;
  margin: 0 5px 5px 0;
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 5px;

  background-color: pink;
}

.keyboard li:hover {
  position: relative;
  border-color: gray;
  cursor: pointer;
}
.keyboard li:active {
  top: 1px;
  left: 1px;
}

.keyboard .tab,
.keyboard .delete {
  width: 70px;
}
.keyboard .capslock {
  width: 80px;
}
.keyboard .enter {
  width: 77px;
}
.keyboard .shift {
  width: 102px;
}
.keyboard .space {
  clear: left;
  width: 660px;
}
.keyboard .shifted {
  position: relative;
  top: 1px;
  left: 1px;
  border-color: #e5e5e5;
  cursor: pointer;
}
.keyboard .capsed {
  position: relative;
  top: 1px;
  left: 1px;
  border-color: #e5e5e5;
  cursor: pointer;
}
</style>