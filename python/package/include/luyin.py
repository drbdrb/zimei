class Luyin():
    '''录音类'''

    def success(self,results):
        pass

    def error(self,bug):
        print(bug)

    '''
    录音主函数
    参数：
        Location -- 录音保存文件
        Stop_time -- 录音时长（秒）
        p_self -- 主进程对象（可提高代码运行效率）
    '''
    def main(self,Stop_time, p_self):
        try:

            got_a_sentence = False
            leave = False

            #停止录音
            def handle_int(sig, chunk):
                global leave, got_a_sentence
                leave = True
                got_a_sentence = True


            def record_to_file( data, sample_width):
                #“从麦克风记录并输出结果数据到‘path’”
               # sample_width, data = record()
                data = p_self.pack('<' + ('h' * len(data)), *data)
                # wf = p_self.wave.open("/keyicx/python/data/yuyin/wo.wav", 'wb')
                # wf.setnchannels(1)
                # wf.setsampwidth(sample_width)
                # wf.setframerate(p_self.RATE)
                # wf.writeframes(data)
                # wf.close()              
                return data


            def normalize(snd_data):
                "平均音量"
                MAXIMUM = 32767  # 16384
                times = float(MAXIMUM) / max(abs(i) for i in snd_data)
                r = p_self.array('h')
                for i in snd_data:
                    r.append(int(i * times))
                return r

            #捕获 Ctrl+C 信号 停止录音
            p_self.signal.signal(p_self.signal.SIGINT, handle_int)

            while not leave:
                ring_buffer           = p_self.collections.deque(maxlen = p_self.NUM_PADDING_CHUNKS)
                triggered             = False
                ring_buffer_flags     = [0] * p_self.NUM_WINDOW_CHUNKS
                ring_buffer_index     = 0

                ring_buffer_flags_end = [0] * p_self.NUM_WINDOW_CHUNKS_END
                ring_buffer_index_end = 0
                
                # WangS
                raw_data              = p_self.array('h')
                index                 = 0
                start_point           = 0
                StartTime             = p_self.time.time()
                #log.info("* recording: ")
                p_self.stream.start_stream()

                #p_self.sys.stdout.write('start')
                p_self.sw.sendmic('start')

                while not got_a_sentence and not leave:
                    chunk = p_self.stream.read(p_self.CHUNK_SIZE,exception_on_overflow = False)#debug溢出
                    # add WangS
                    raw_data.extend(p_self.array('h', chunk))
                    index += p_self.CHUNK_SIZE
                    TimeUse = p_self.time.time() - StartTime

                    active = p_self.vad.is_speech(chunk, p_self.RATE)

                    #p_self.sys.stdout.write('1' if active else '_')
                    p_self.sw.sendmic('1' if active else '0')

                    ring_buffer_flags[ring_buffer_index] = 1 if active else 0
                    ring_buffer_index += 1
                    ring_buffer_index %= p_self.NUM_WINDOW_CHUNKS

                    ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
                    ring_buffer_index_end += 1
                    ring_buffer_index_end %= p_self.NUM_WINDOW_CHUNKS_END

                    # start point detection起始点检测
                    if not triggered:
                        ring_buffer.append(chunk)
                        num_voiced = sum(ring_buffer_flags)
                        if num_voiced > 0.8 * p_self.NUM_WINDOW_CHUNKS:
                            #p_self.sys.stdout.write(' Open ')
                            p_self.sw.sendmic('open')

                            triggered = True
                            start_point = index - p_self.CHUNK_SIZE * 20  # start point
                            # voiced_frames.extend(ring_buffer)
                            ring_buffer.clear()
                        elif TimeUse > Stop_time:#录音时间
                            #p_self.sys.stdout.write(' Close ')
                            p_self.sw.sendmic('close')

                            triggered = False
                            got_a_sentence = True
                    # end point detection端点检测
                    else:
                        # voiced_frames.append(chunk)
                        ring_buffer.append(chunk)
                        num_unvoiced = p_self.NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)

                        if num_unvoiced > 0.90 * p_self.NUM_WINDOW_CHUNKS_END or TimeUse > Stop_time:     #录音时间
                            #录音时间必须大于2秒
                            if TimeUse >2:
                                #p_self.sys.stdout.write(' Close ')
                                p_self.sw.sendmic('close')

                                triggered = False
                                got_a_sentence = True

                    #p_self.sys.stdout.flush()       #输出缓冲区内容

                p_self.stream.stop_stream()

                p_self.sw.sendmic('stop')

                #log.info("* done recording")
                got_a_sentence = False

                # 写入文件
                raw_data.reverse()
                for index in range(start_point):
                    raw_data.pop()
                raw_data.reverse()
                raw_data = normalize(raw_data)
                #record_to_file("recording.wav", raw_data, 2)
                results =record_to_file( raw_data, 2)
                leave = True

            p_self.stream.close()
            self.success(results)
        except Exception as bug:
            self.error(bug)


if __name__ == '__main__':
    Luyin().main("recording.wav",10)