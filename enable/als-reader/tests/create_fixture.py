"""Generate a minimal but realistic .als test fixture."""
import gzip
import os

ALS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<Ableton MajorVersion="5" MinorVersion="11.0.12" SchemaChangeCount="3" Creator="Ableton Live 11.3.13" Revision="">
  <LiveSet>
    <NextPointeeId Value="20000" />
    <OverwriteProtectionNumber Value="2819" />
    <LomId Value="0" />
    <LomIdView Value="0" />
    <IsContentSelected Value="true" />
    <Transport>
      <LoopOn Value="true" />
      <LoopStart Value="0" />
      <LoopLength Value="16" />
      <CurrentTime Value="4.5" />
      <PunchIn Value="false" />
      <PunchOut Value="false" />
      <MetronomeOn Value="false" />
      <DrawMode Value="false" />
    </Transport>
    <MasterTrack>
      <LomId Value="0" />
      <Name>
        <EffectiveName Value="Master" />
        <UserName Value="" />
      </Name>
      <Color Value="0" />
      <DeviceChain>
        <Mixer>
          <Volume>
            <Manual Value="0.7" />
            <AutomationTarget Id="1" />
          </Volume>
          <Pan>
            <Manual Value="0" />
            <AutomationTarget Id="2" />
          </Pan>
          <Tempo>
            <Manual Value="128" />
            <AutomationTarget Id="3" />
          </Tempo>
          <TimeSignature>
            <TimeSignatures>
              <RemoteableTimeSignature Id="0">
                <Numerator Value="4" />
                <Denominator Value="4" />
                <Time Value="0" />
              </RemoteableTimeSignature>
            </TimeSignatures>
          </TimeSignature>
          <CrossFade Value="0" />
          <Speaker Value="true" />
          <SoloSink Value="false" />
        </Mixer>
        <DeviceChain>
          <Devices>
            <Limiter Id="0">
              <LomId Value="0" />
              <IsExpanded Value="true" />
              <On>
                <Manual Value="true" />
              </On>
              <ParametersListWrapper LomId="0" />
              <Ceiling Value="-0.3" />
              <Release Value="10" />
              <Gain Value="0" />
            </Limiter>
          </Devices>
        </DeviceChain>
        <AutomationEnvelopes>
          <Envelopes>
            <AutomationEnvelope Id="0">
              <EnvelopeTarget>
                <PointeeId Value="3" />
              </EnvelopeTarget>
              <Automation>
                <Events>
                  <AutomationEvent Id="0" Time="0" Value="128" />
                  <AutomationEvent Id="1" Time="8" Value="130" />
                  <AutomationEvent Id="2" Time="12" Value="126" />
                </Events>
              </Automation>
            </AutomationEnvelope>
          </Envelopes>
        </AutomationEnvelopes>
      </DeviceChain>
    </MasterTrack>
    <Tracks>
      <MidiTrack Id="1">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Bass Synth" />
          <UserName Value="Bass Synth" />
          <Annotation Value="" />
          <MemorizedFirstClipName Value="" />
        </Name>
        <Color Value="13" />
        <TrackGroupId Value="-1" />
        <TrackUnfolded Value="true" />
        <IsFolded Value="false" />
        <Freeze Value="false" />
        <DeviceChain>
          <AudioInputRouting>
            <Target Value="AudioIn/External/S0" />
            <UpperDisplayString Value="Ext. In" />
            <LowerDisplayString Value="1/2" />
          </AudioInputRouting>
          <MidiInputRouting>
            <Target Value="MidiIn/External.All/-1" />
            <UpperDisplayString Value="Ext: All Ins" />
            <LowerDisplayString Value="" />
          </MidiInputRouting>
          <AudioOutputRouting>
            <Target Value="AudioOut/Master" />
            <UpperDisplayString Value="Master" />
            <LowerDisplayString Value="" />
          </AudioOutputRouting>
          <MidiOutputRouting>
            <Target Value="MidiOut/None" />
            <UpperDisplayString Value="None" />
            <LowerDisplayString Value="" />
          </MidiOutputRouting>
          <Mixer>
            <LomId Value="0" />
            <Volume>
              <Manual Value="0.85" />
              <AutomationTarget Id="100" />
            </Volume>
            <Pan>
              <Manual Value="-0.1" />
              <AutomationTarget Id="101" />
            </Pan>
            <SendsListPreset>
              <SendPreset>
                <Send>
                  <Manual Value="0.5" />
                  <AutomationTarget Id="102" />
                </Send>
                <Active Value="true" />
              </SendPreset>
              <SendPreset>
                <Send>
                  <Manual Value="0.2" />
                  <AutomationTarget Id="103" />
                </Send>
                <Active Value="true" />
              </SendPreset>
            </SendsListPreset>
            <Speaker Value="true" />
            <SoloSink Value="false" />
            <Solo Value="false" />
            <CrossFadeState Value="0" />
          </Mixer>
          <MainSequencer>
            <ClipTimeable>
              <ArrangerAutomation>
                <Events>
                  <MidiClip Id="0" Time="0">
                    <LomId Value="0" />
                    <Name Value="Bass Pattern" />
                    <Color Value="3" />
                    <CurrentStart Value="0" />
                    <CurrentEnd Value="4" />
                    <Loop>
                      <LoopOn Value="true" />
                      <LoopStart Value="0" />
                      <LoopEnd Value="4" />
                      <StartRelative Value="0" />
                      <OutMarker Value="4" />
                      <HiddenLoopStart Value="0" />
                      <HiddenLoopEnd Value="4" />
                    </Loop>
                    <IsWarped Value="true" />
                    <Notes>
                      <KeyTracks>
                        <KeyTrack Id="0">
                          <MidiKey Value="36" />
                          <Notes>
                            <MidiNoteEvent Time="0" Duration="0.5" Velocity="100" VelocityDeviation="0" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="1" />
                            <MidiNoteEvent Time="1" Duration="0.5" Velocity="90" VelocityDeviation="0" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="2" />
                            <MidiNoteEvent Time="2" Duration="0.25" Velocity="110" VelocityDeviation="0" OffVelocity="64" Probability="0.75" IsEnabled="true" NoteId="3" />
                            <MidiNoteEvent Time="3" Duration="0.5" Velocity="95" VelocityDeviation="0" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="4" />
                          </Notes>
                        </KeyTrack>
                        <KeyTrack Id="1">
                          <MidiKey Value="48" />
                          <Notes>
                            <MidiNoteEvent Time="2" Duration="1" Velocity="80" VelocityDeviation="5" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="5" />
                          </Notes>
                        </KeyTrack>
                      </KeyTracks>
                      <PerNoteEventStore />
                    </Notes>
                    <Envelopes>
                      <Envelopes>
                        <ClipEnvelope Id="0">
                          <EnvelopeTarget>
                            <PointeeId Value="100" />
                          </EnvelopeTarget>
                          <Automation>
                            <Events>
                              <AutomationEvent Id="0" Time="0" Value="0.5" />
                              <AutomationEvent Id="1" Time="2" Value="0.8" />
                            </Events>
                          </Automation>
                        </ClipEnvelope>
                      </Envelopes>
                    </Envelopes>
                  </MidiClip>
                  <MidiClip Id="1" Time="4">
                    <LomId Value="0" />
                    <Name Value="Bass Fill" />
                    <Color Value="3" />
                    <CurrentStart Value="4" />
                    <CurrentEnd Value="8" />
                    <Loop>
                      <LoopOn Value="false" />
                      <LoopStart Value="0" />
                      <LoopEnd Value="4" />
                      <StartRelative Value="0" />
                      <OutMarker Value="4" />
                      <HiddenLoopStart Value="0" />
                      <HiddenLoopEnd Value="4" />
                    </Loop>
                    <Notes>
                      <KeyTracks>
                        <KeyTrack Id="0">
                          <MidiKey Value="36" />
                          <Notes>
                            <MidiNoteEvent Time="0" Duration="0.25" Velocity="120" VelocityDeviation="0" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="10" />
                            <MidiNoteEvent Time="0.5" Duration="0.25" Velocity="115" VelocityDeviation="0" OffVelocity="64" Probability="1" IsEnabled="true" NoteId="11" />
                          </Notes>
                        </KeyTrack>
                      </KeyTracks>
                    </Notes>
                  </MidiClip>
                </Events>
              </ArrangerAutomation>
            </ClipTimeable>
            <ClipSlotList>
              <ClipSlot Id="0">
                <ClipSlot>
                  <Value>
                    <MidiClip Id="10" Time="0">
                      <LomId Value="0" />
                      <Name Value="Session Bass" />
                      <Color Value="5" />
                      <CurrentStart Value="0" />
                      <CurrentEnd Value="4" />
                      <Loop>
                        <LoopOn Value="true" />
                        <LoopStart Value="0" />
                        <LoopEnd Value="4" />
                      </Loop>
                      <Notes>
                        <KeyTracks>
                          <KeyTrack Id="0">
                            <MidiKey Value="36" />
                            <Notes>
                              <MidiNoteEvent Time="0" Duration="1" Velocity="100" NoteId="20" />
                            </Notes>
                          </KeyTrack>
                        </KeyTracks>
                      </Notes>
                      <LaunchMode Value="0" />
                      <LaunchQuantization Value="4" />
                      <Legato Value="false" />
                      <FollowAction>
                        <FollowTime Value="4" />
                        <IsLinked Value="true" />
                        <LoopIterations Value="1" />
                        <FollowActionEnabled Value="true" />
                        <FollowActionA Value="1" />
                        <FollowActionB Value="0" />
                        <FollowChanceA Value="100" />
                        <FollowChanceB Value="0" />
                      </FollowAction>
                    </MidiClip>
                  </Value>
                  <HasStop Value="true" />
                </ClipSlot>
              </ClipSlot>
              <ClipSlot Id="1">
                <ClipSlot>
                  <Value />
                  <HasStop Value="true" />
                </ClipSlot>
              </ClipSlot>
            </ClipSlotList>
          </MainSequencer>
          <DeviceChain>
            <Devices>
              <OriginalSimpler Id="0">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <ParametersListWrapper LomId="0" />
              </OriginalSimpler>
              <Eq8 Id="1">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <ParametersListWrapper LomId="0" />
                <Mode Value="0" />
              </Eq8>
              <Compressor2 Id="2">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="false" />
                </On>
                <ParametersListWrapper LomId="0" />
                <Threshold Value="-20" />
                <Ratio Value="4" />
                <Attack Value="10" />
                <Release Value="100" />
                <Gain Value="0" />
                <DryWet Value="1" />
              </Compressor2>
              <PluginDevice Id="3">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <PluginDesc>
                  <VstPluginInfo>
                    <PlugName Value="Serum" />
                    <Category Value="Instrument" />
                    <Vendor Value="Xfer Records" />
                    <UniqueId Value="1397572658" />
                  </VstPluginInfo>
                </PluginDesc>
              </PluginDevice>
            </Devices>
          </DeviceChain>
          <AutomationEnvelopes>
            <Envelopes>
              <AutomationEnvelope Id="0">
                <EnvelopeTarget>
                  <PointeeId Value="100" />
                </EnvelopeTarget>
                <Automation>
                  <Events>
                    <AutomationEvent Id="0" Time="0" Value="0.85" />
                    <AutomationEvent Id="1" Time="4" Value="0.6" />
                    <AutomationEvent Id="2" Time="8" Value="0.9" />
                  </Events>
                </Automation>
              </AutomationEnvelope>
            </Envelopes>
          </AutomationEnvelopes>
        </DeviceChain>
      </MidiTrack>
      <AudioTrack Id="2">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Drums" />
          <UserName Value="Drums" />
          <Annotation Value="" />
        </Name>
        <Color Value="21" />
        <TrackGroupId Value="-1" />
        <Freeze Value="false" />
        <DeviceChain>
          <AudioInputRouting>
            <Target Value="AudioIn/External/S0" />
            <UpperDisplayString Value="Ext. In" />
            <LowerDisplayString Value="1/2" />
          </AudioInputRouting>
          <AudioOutputRouting>
            <Target Value="AudioOut/Master" />
            <UpperDisplayString Value="Master" />
            <LowerDisplayString Value="" />
          </AudioOutputRouting>
          <Mixer>
            <Volume>
              <Manual Value="0.9" />
              <AutomationTarget Id="200" />
            </Volume>
            <Pan>
              <Manual Value="0" />
              <AutomationTarget Id="201" />
            </Pan>
            <SendsListPreset>
              <SendPreset>
                <Send>
                  <Manual Value="0.3" />
                  <AutomationTarget Id="202" />
                </Send>
                <Active Value="true" />
              </SendPreset>
            </SendsListPreset>
            <Speaker Value="true" />
            <Solo Value="false" />
          </Mixer>
          <MainSequencer>
            <Sample>
              <ArrangerAutomation>
                <Events>
                  <AudioClip Id="0" Time="0">
                    <LomId Value="0" />
                    <Name Value="Break_120bpm" />
                    <Color Value="9" />
                    <CurrentStart Value="0" />
                    <CurrentEnd Value="8" />
                    <Loop>
                      <LoopOn Value="true" />
                      <LoopStart Value="0" />
                      <LoopEnd Value="8" />
                    </Loop>
                    <IsWarped Value="true" />
                    <WarpMode Value="3" />
                    <SampleRef>
                      <FileRef>
                        <RelativePath Value="Samples/Imported/Break_120bpm.wav" />
                        <Path Value="/Users/producer/Music/Ableton/Project/Samples/Imported/Break_120bpm.wav" />
                        <Type Value="1" />
                        <LivePackName Value="" />
                        <LivePackId Value="" />
                      </FileRef>
                      <DefaultDuration Value="352800" />
                      <DefaultSampleRate Value="44100" />
                    </SampleRef>
                    <WarpMarkers>
                      <WarpMarker SecTime="0" BeatTime="0" />
                      <WarpMarker SecTime="4" BeatTime="8" />
                    </WarpMarkers>
                    <Gain Value="1" />
                    <PitchCoarse Value="0" />
                    <PitchFine Value="0" />
                  </AudioClip>
                </Events>
              </ArrangerAutomation>
            </Sample>
            <ClipSlotList />
          </MainSequencer>
          <DeviceChain>
            <Devices>
              <Eq8 Id="0">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
              </Eq8>
              <AudioEffectGroupDevice Id="1">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <Branches>
                  <AudioEffectBranch Id="0">
                    <Name Value="Chain A" />
                    <DeviceChain>
                      <Devices>
                        <Compressor2 Id="0">
                          <LomId Value="0" />
                          <On>
                            <Manual Value="true" />
                          </On>
                        </Compressor2>
                      </Devices>
                    </DeviceChain>
                  </AudioEffectBranch>
                </Branches>
                <Macros>
                  <Macro0>
                    <MacroName Value="Macro 1" />
                    <Manual Value="64" />
                  </Macro0>
                  <Macro1>
                    <MacroName Value="Macro 2" />
                    <Manual Value="0" />
                  </Macro1>
                </Macros>
              </AudioEffectGroupDevice>
              <AuPluginDevice Id="2">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <PluginDesc>
                  <AuPluginInfo>
                    <Name Value="FabFilter Pro-Q 3" />
                    <Manufacturer Value="FabFilter" />
                  </AuPluginInfo>
                </PluginDesc>
              </AuPluginDevice>
            </Devices>
          </DeviceChain>
        </DeviceChain>
      </AudioTrack>
      <GroupTrack Id="3">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Music Group" />
          <UserName Value="Music Group" />
        </Name>
        <Color Value="5" />
        <TrackGroupId Value="-1" />
        <DeviceChain>
          <Mixer>
            <Volume>
              <Manual Value="1.0" />
            </Volume>
            <Pan>
              <Manual Value="0" />
            </Pan>
            <Speaker Value="true" />
            <Solo Value="false" />
          </Mixer>
        </DeviceChain>
      </GroupTrack>
      <MidiTrack Id="4">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Lead" />
          <UserName Value="Lead" />
        </Name>
        <Color Value="7" />
        <TrackGroupId Value="3" />
        <Freeze Value="false" />
        <DeviceChain>
          <AudioOutputRouting>
            <Target Value="AudioOut/GroupTrack" />
            <UpperDisplayString Value="Music Group" />
            <LowerDisplayString Value="" />
          </AudioOutputRouting>
          <Mixer>
            <Volume>
              <Manual Value="0.75" />
            </Volume>
            <Pan>
              <Manual Value="0.2" />
            </Pan>
            <Speaker Value="true" />
            <Solo Value="true" />
          </Mixer>
          <MainSequencer>
            <ClipTimeable>
              <ArrangerAutomation>
                <Events />
              </ArrangerAutomation>
            </ClipTimeable>
            <ClipSlotList />
          </MainSequencer>
          <DeviceChain>
            <Devices>
              <InstrumentGroupDevice Id="0">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <Branches>
                  <InstrumentBranch Id="0">
                    <Name Value="Pad Layer" />
                    <DeviceChain>
                      <Devices>
                        <OriginalSimpler Id="0">
                          <LomId Value="0" />
                          <On><Manual Value="true" /></On>
                        </OriginalSimpler>
                      </Devices>
                    </DeviceChain>
                  </InstrumentBranch>
                  <InstrumentBranch Id="1">
                    <Name Value="Pluck Layer" />
                    <DeviceChain>
                      <Devices>
                        <PluginDevice Id="0">
                          <LomId Value="0" />
                          <On><Manual Value="true" /></On>
                          <PluginDesc>
                            <VstPluginInfo>
                              <PlugName Value="Vital" />
                              <Category Value="Instrument" />
                              <Vendor Value="Matt Tytel" />
                            </VstPluginInfo>
                          </PluginDesc>
                        </PluginDevice>
                      </Devices>
                    </DeviceChain>
                  </InstrumentBranch>
                </Branches>
              </InstrumentGroupDevice>
            </Devices>
          </DeviceChain>
        </DeviceChain>
      </MidiTrack>
      <ReturnTrack Id="5">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Reverb" />
          <UserName Value="Reverb" />
        </Name>
        <Color Value="1" />
        <DeviceChain>
          <Mixer>
            <Volume>
              <Manual Value="0.6" />
            </Volume>
            <Pan>
              <Manual Value="0" />
            </Pan>
            <Speaker Value="true" />
            <Solo Value="false" />
          </Mixer>
          <DeviceChain>
            <Devices>
              <Reverb Id="0">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
                <DecayTime Value="2500" />
                <DryWet Value="1.0" />
                <RoomSize Value="80" />
              </Reverb>
            </Devices>
          </DeviceChain>
        </DeviceChain>
      </ReturnTrack>
      <ReturnTrack Id="6">
        <LomId Value="0" />
        <Name>
          <EffectiveName Value="Delay" />
          <UserName Value="Delay" />
        </Name>
        <Color Value="2" />
        <DeviceChain>
          <Mixer>
            <Volume>
              <Manual Value="0.5" />
            </Volume>
            <Pan>
              <Manual Value="0" />
            </Pan>
            <Speaker Value="true" />
            <Solo Value="false" />
          </Mixer>
          <DeviceChain>
            <Devices>
              <Delay Id="0">
                <LomId Value="0" />
                <IsExpanded Value="true" />
                <On>
                  <Manual Value="true" />
                </On>
              </Delay>
            </Devices>
          </DeviceChain>
        </DeviceChain>
      </ReturnTrack>
    </Tracks>
    <Scenes>
      <Scene Id="0">
        <Name Value="Intro" />
        <Color Value="0" />
        <Tempo Value="-1" />
        <TimeSignatureId Value="-1" />
        <IsAlwaysLaunchedAfterLoading Value="false" />
        <FollowAction>
          <FollowTime Value="4" />
          <IsLinked Value="false" />
          <FollowActionEnabled Value="false" />
        </FollowAction>
      </Scene>
      <Scene Id="1">
        <Name Value="Drop" />
        <Color Value="13" />
        <Tempo Value="130" />
        <TimeSignatureId Value="-1" />
        <IsAlwaysLaunchedAfterLoading Value="false" />
      </Scene>
    </Scenes>
    <Locators>
      <Locators>
        <Locator Id="0">
          <Time Value="0" />
          <Name Value="Intro" />
          <Annotation Value="" />
          <IsSongStart Value="true" />
        </Locator>
        <Locator Id="1">
          <Time Value="8" />
          <Name Value="Build" />
          <Annotation Value="" />
          <IsSongStart Value="false" />
        </Locator>
        <Locator Id="2">
          <Time Value="16" />
          <Name Value="Drop" />
          <Annotation Value="" />
          <IsSongStart Value="false" />
        </Locator>
      </Locators>
    </Locators>
    <ScaleInformation>
      <RootNote Value="0" />
      <Name Value="Major" />
    </ScaleInformation>
    <GroovePool>
      <Grooves>
        <Groove Id="0">
          <Name Value="MPC 16 Swing-62" />
          <Base Value="0.25" />
          <Quantize Value="0.5" />
          <Timing Value="0.8" />
          <Random Value="0" />
          <Velocity Value="0" />
        </Groove>
      </Grooves>
    </GroovePool>
  </LiveSet>
</Ableton>
"""

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "test_project.als")
    with gzip.open(out, "wb") as f:
        f.write(ALS_XML.encode("utf-8"))
    print(f"Created {out}")
